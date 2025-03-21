from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
import uvicorn
import json
from openai import OpenAI

app = FastAPI(title="LLM Chat Template")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# In-memory chat history storage
chat_history: Dict[str, List[Dict[str, str]]] = {}

def chat_answer(messages):
    completion = client.chat.completions.create(
        model="TheBloke/dolphin-2.2.1-mistral-7B-GGUF",
        messages=messages,
        temperature=1.1,
        max_tokens=140,
        stream=True,  # Enable streaming
    )
    return completion
def chat_answer_gemini(message):

    client = genai.GenerativeModel(model_name="gemini-2.0-flash")
    # Format the message for Gemini
    prompt = message[-1]["content"] if message else "Hello"
    # Include context from previous messages if available
    if len(message) > 1:
        context = " ".join([m["content"] for m in message[:-1]])
        prompt = f"Context: {context}\n\nQuestion: {prompt}"
    
    response = client.generate_content(prompt, stream=True)
    
    for chunk in response:
        if hasattr(chunk, 'text'):
            yield chunk.text


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    message = data.get("message")
    
    # Initialize session if it doesn't exist
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    # Add user message to history
    chat_history[session_id].append({"role": "user", "content": message})
    
    # Return the user message immediately to confirm receipt
    return {"status": "message received", "user_message": message}

@app.get("/stream/{session_id}")
async def stream_response(session_id: str, model: str = "openai"):
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

async def generate_stream(session_id, messages, model="openai"):
    # Get streaming response from LLM based on model choice
    try:
        full_response = ""
        
        if model == "gemini":
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

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    if session_id not in chat_history:
        return {"history": []}
    return {"history": chat_history[session_id]}

@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    if session_id in chat_history:
        chat_history[session_id] = []
    return {"status": "history cleared"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)