# AI Chat Assistant

A beautiful AI chat interface with Python backend, featuring an animated glowing orb design.

## Features

- 🤖 Simple AI chatbot with basic conversation capabilities
- 💬 Handles greetings, farewells, time/date queries, and more
- 🎨 Beautiful animated UI with glowing orb effect
- 🌐 Flask web server with REST API
- 📱 Responsive design for mobile and desktop

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

- Type your message in the input field
- Press Enter or click the send button
- The AI will respond based on its training

## Training Data

The chatbot can respond to:
- Greetings (hi, hello, hey)
- How are you questions
- Name and identity queries
- Time and date requests
- Goodbye messages
- Thank you messages
- Help requests
- And more!

## Project Structure

```
first ai/
├── app.py              # Flask server
├── chatbot.py          # Chatbot logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Main HTML page
└── static/
    ├── style.css      # Styling
    └── script.js      # Frontend JavaScript
```

## Customization

You can extend the chatbot by adding more patterns in `chatbot.py`:

```python
'your_category': {
    'patterns': [r'\b(your|pattern|here)\b'],
    'responses': ['Your response here']
}
```

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Custom CSS animations and gradients
