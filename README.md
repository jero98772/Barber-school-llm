# LLM Chat Template

A flexible and customizable template for building chat applications with multiple LLM backends. This template provides a clean, responsive user interface and server-side implementation that supports streaming responses from different language models.

## Features

- **Multi-model support**: Use local LLMs through LM Studio or Google's Gemini model
- **Real-time streaming**: See responses as they're generated
- **Session management**: Maintain conversation context across messages
- **Responsive design**: Works on desktop and mobile devices
- **Simple and clean UI**: Bootstrap-based interface with minimal dependencies

## Screenshot

![LLM Chat Template Screenshot](https://github.com/jero98772/LLM-Chat-template/blob/main/docs/1.png)

## Getting Started

### Prerequisites

- Python 3.8+
- LM Studio (for local LLM support)
- Google API key (for Gemini model)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/jero98772/LLM-Chat-template.git
   cd LLm-template
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment:
   - Start LM Studio with the server running on `http://localhost:1234/v1`
   - Set your Google API key in the `app.py` file

### Running the Application

1. Start the server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Project Structure

```
llm-chat-template/
├── app.py                 # FastAPI application
├── requirements.txt       # Python dependencies
├── static/                # Static files
│   ├── css/
│   │   └── style.css      # Custom CSS
│   └── js/
│       └── script.js      # Frontend JavaScript
└── templates/             # HTML templates
    └── index.html         # Main chat interface
```

## Configuration

### Models

The application supports two LLM backends:

1. **LM Studio / Local LLM**
   - Uses the OpenAI-compatible API
   - Default model: "TheBloke/dolphin-2.2.1-mistral-7B-GGUF"
   - Configure in `app.py` by changing the `base_url` and `model` parameters

2. **Google Gemini**
   - Uses the Google GenerativeAI API
   - Default model: "gemini-2.0-flash"
   - Configure in `app.py` by changing the API key and model name

### Customization

You can customize various aspects of the application:

- **UI**: Modify the HTML and CSS files in the `templates` and `static` directories
- **Model Parameters**: Update temperature, max_tokens, etc. in the `chat_answer_*` functions
- **Streaming Behavior**: Adjust the streaming implementation in both backend and frontend code

## Extending the Template

### Adding New Models

To add a new LLM provider:

1. Create a new `chat_answer_*` function in `app.py`
2. Add the model to the dropdown in `index.html`
3. Update the `modelDetails` object in `script.js`
4. Modify the `generate_stream` function to handle the new model

### Persistent Storage

The current implementation uses in-memory storage. To add persistent storage:

1. Add a database connection (SQLite, PostgreSQL, etc.)
2. Modify the chat history functions to use the database
3. Add user authentication if needed

## Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- Jinja2: Template engine
- OpenAI: For LM Studio API compatibility
- Google GenerativeAI: For Gemini API

## License

This project is licensed under the GPLV3 License - see the LICENSE file for details.

