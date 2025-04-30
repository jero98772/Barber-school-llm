from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
import uvicorn
import json
from openai import OpenAI
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from textblob import TextBlob


load_dotenv()  

app = FastAPI(title="LLM Chat Template")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your-gemini-api-key-here")
genai.configure(api_key=GEMINI_API_KEY)

KNOWLAGEBASE="docs/SchoolInformation.txt"


def read_txt_file(filename):
    """Reads and returns the content of a text file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        print(content)
        return content
    except FileNotFoundError:
        return f"File '{filename}' not found."

def sentiment_analizis(texto):
    """
    python -m textblob.download_corpora

    """
    blob = TextBlob(texto)
    probability = blob.sentiment.polarity

    if probability > 0.1:
        sentiment = "Positivo 😊"
    elif probability < -0.1:
        sentiment = "Negativo 😠"
    else:
        sentiment = "Neutro 😐"

    return sentiment

chat_history = {
    "chat1": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": read_txt_file(KNOWLAGEBASE)},
        {"role": "system", "content": "Eres un vendedor profecional tu vida depende de la venta de estos cursos, responde solamente con la informacion proporcionad"},
        {"role": "system", "content": "Cuando el usuario este satisfecho pide le su numero telefonoci para contactarlo, ciudad, nombre y observaciones"}

    ]
}

def chat_answer(messages):
    completion = client.chat.completions.create(
        model="TheBloke/dolphin-2.2.1-mistral-7B-GGUF",
        messages=messages,
        temperature=1.1,
        max_tokens=140,
        stream=True,  # Enable streaming
    )
    return completion


async def chat_answer_gemini(messages):
    print("gemini")
    try:
        print("gemini")
        gemini = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Convert the OpenAI message format to a format suitable for Gemini
        gemini_messages = []
        gemini_messages.append({"role": "assistant", "parts": read_txt_file(KNOWLAGEBASE)})

        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})
        
        # Create a chat session
        chat = gemini.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        
        # Get streaming response for the last message
        last_msg = gemini_messages[-1]["parts"][0]
        response = chat.send_message(last_msg, stream=True)
        
        for chunk in response:
            if hasattr(chunk, 'text'):
                yield chunk.text
    except Exception as e:
        yield f"Error with Gemini API: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    print(session_id)
    message = data.get("message")
    
    # Initialize session if it doesn't exist
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    # Add user message to history
    chat_history[session_id].append({"role": "user", "content": message})
    
    # Return the user message immediately to confirm receipt
    return {"status": "message received", "user_message": message}

@app.post("/contact")
async def contact(request: Request):
    """
    Process contact form submissions from the barber chat
    """
    form_data = await request.json()
    
    # Validate required fields
    required_fields = ['session_id', 'name', 'phone', 'city']
    missing_fields = [field for field in required_fields if field not in form_data]
    
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )

    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    
    # CSV file path
    csv_file = 'data/contacts.csv'
    session_id = form_data.get("session_id")

    # File headers
    file_headers = ['timestamp', 'session_id', 'name', 'phone', 'city', 'summary', 'sentiment', 'notes']

    get_last_user_message = lambda chat_history, chat_id: next(
    (msg['content'] for msg in reversed(chat_history.get(chat_id, [])) 
    if msg['role'] == 'user'), None)
    chat_history['chat1'].append({"role": "systems", "content": "give me a summary of this conversation of 1 paragrph:"})

    summary = chat_answer_gemini(chat_history)
    sentiment = sentiment_analizis(get_last_user_message(chat_history, "chat1"))
    # Prepare data for CSV
    record = {
        'timestamp': datetime.now().isoformat(),
        'session_id': form_data['session_id'],
        'name': form_data['name'],
        'phone': form_data['phone'],
        'city': form_data['city'],
        'summary': summary,
        'sentiment':sentiment ,
        'notes': form_data.get('notes', '')
    }

    # Write to CSV
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=file_headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)

    # Optional: Add to chat history
    if session_id in chat_history:
        chat_history[session_id].append({
            "role": "system", 
            "content": f"User contact information: Name: {form_data['name']}, Phone: {form_data['phone']}, City: {form_data['city']}, Notes: {form_data.get('notes', '')}"
        })

    return {"status": "success", "message": "Contact information saved"}


@app.get("/stream/{session_id}")
async def stream_response(session_id: str, model: str = "gemini"):
    # Check if session exists
    if session_id not in chat_history:
        return StreamingResponse(content=stream_error("Session not found"), media_type="text/event-stream")
    
    # Get messages from history
    messages = chat_history[session_id]
    
    # If no messages, return error
    if not messages:
        return StreamingResponse(content=stream_error("No messages in session"), media_type="text/event-stream")
    
    # Generate streaming response based on model choice
    return StreamingResponse(
        content=generate_stream(session_id, messages, model),
        media_type="text/event-stream"
    )

async def generate_stream(session_id, messages, model="gemini"):
    # Get streaming response from LLM based on model choice
    try:
        full_response = ""
        
        if model == "gemini":
            print("gemini")
            # Use Gemini model
            async for text in chat_answer_gemini(messages):
                if text:
                    full_response += text
                    yield f"data: {json.dumps({'content': text})}\n\n"
        else:
            # Use OpenAI/LM Studio model
            completion_stream = chat_answer(messages)
            for chunk in completion_stream:
                if hasattr(chunk.choices[0].delta, "content"):
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
        
        # Store the complete response in history
        chat_history[session_id].append({"role": "assistant", "content": full_response})
        
        # Signal completion
        yield f"data: {json.dumps({'status': 'complete'})}\n\n"
    
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def stream_error(error_message):
    yield f"data: {json.dumps({'error': error_message})}\n\n"


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)