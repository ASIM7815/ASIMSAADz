import random
import re
from datetime import datetime

class SimpleChatbot:
    def __init__(self):
        # Training data for greetings and basic conversations
        self.patterns = {
            'greeting': {
                'patterns': [
                    r'\b(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b',
                ],
                'responses': [
                    "Hello! How can I help you today?",
                    "Hi there! What can I do for you?",
                    "Hey! Nice to meet you. How can I assist you?",
                    "Greetings! I'm here to help. What do you need?",
                ]
            },
            'how_are_you': {
                'patterns': [
                    r'\b(how are you|how\'re you|how are u|hows it going|whats up)\b',
                ],
                'responses': [
                    "I'm doing great, thank you for asking! How can I help you?",
                    "I'm functioning perfectly! What can I do for you today?",
                    "I'm doing well! Ready to assist you with anything you need.",
                ]
            },
            'name': {
                'patterns': [
                    r'\b(what is your name|what\'s your name|who are you|your name)\b',
                ],
                'responses': [
                    "I'm an AI assistant created to help you. You can call me ChatBot!",
                    "I'm ChatBot, your friendly AI assistant. How can I help you?",
                    "My name is ChatBot. I'm here to assist you with your questions!",
                ]
            },
            'age': {
                'patterns': [
                    r'\b(how old are you|what is your age|your age)\b',
                ],
                'responses': [
                    "I'm an AI, so I don't have an age in the traditional sense!",
                    "I was created recently, but age doesn't really apply to AI like me.",
                    "I'm timeless! But I'm always learning and improving.",
                ]
            },
            'time': {
                'patterns': [
                    r'\b(what time|current time|time is it|what\'s the time)\b',
                ],
                'responses': [
                    f"The current time is {datetime.now().strftime('%I:%M %p')}",
                ]
            },
            'date': {
                'patterns': [
                    r'\b(what date|current date|today\'s date|what day)\b',
                ],
                'responses': [
                    f"Today is {datetime.now().strftime('%B %d, %Y')}",
                ]
            },
            'goodbye': {
                'patterns': [
                    r'\b(bye|goodbye|see you|farewell|take care|gotta go)\b',
                ],
                'responses': [
                    "Goodbye! Have a great day!",
                    "See you later! Take care!",
                    "Bye! Feel free to come back anytime!",
                    "Farewell! It was nice chatting with you!",
                ]
            },
            'thanks': {
                'patterns': [
                    r'\b(thank you|thanks|thx|appreciate it)\b',
                ],
                'responses': [
                    "You're welcome! Happy to help!",
                    "No problem! Anytime!",
                    "Glad I could assist you!",
                    "You're welcome! Let me know if you need anything else!",
                ]
            },
            'help': {
                'patterns': [
                    r'\b(help|assist|support|can you help)\b',
                ],
                'responses': [
                    "Of course! I can chat with you, answer questions, and have conversations. Just ask me anything!",
                    "I'm here to help! You can ask me about the time, date, or just have a friendly conversation.",
                    "I'd be happy to help! Try greeting me, asking about the time, or just chatting!",
                ]
            },
            'capabilities': {
                'patterns': [
                    r'\b(what can you do|your capabilities|what do you do)\b',
                ],
                'responses': [
                    "I can chat with you, answer basic questions, tell you the time and date, and have friendly conversations!",
                    "I'm designed to be a conversational AI. I can greet you, answer questions, and chat about various topics!",
                ]
            },
            'weather': {
                'patterns': [
                    r'\b(weather|temperature|forecast)\b',
                ],
                'responses': [
                    "I don't have access to real-time weather data, but I hope it's nice where you are!",
                    "I can't check the weather right now, but you might want to look outside or check a weather app!",
                ]
            },
        }
        
        # Default responses when no pattern matches
        self.default_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "Interesting! Tell me more about that.",
            "I'm still learning. Can you ask me something else?",
            "That's a good question! I'm a simple chatbot, so I might not know everything yet.",
            "Hmm, I don't have a good answer for that. Try asking me about greetings, time, or how I can help!",
        ]
    
    def get_response(self, user_input):
        """
        Process user input and return appropriate response
        """
        if not user_input or user_input.strip() == "":
            return "Please say something!"
        
        # Convert to lowercase for pattern matching
        user_input_lower = user_input.lower()
        
        # Check each pattern category
        for category, data in self.patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, user_input_lower):
                    # Special handling for time/date to get current values
                    if category == 'time':
                        return f"The current time is {datetime.now().strftime('%I:%M %p')}"
                    elif category == 'date':
                        return f"Today is {datetime.now().strftime('%B %d, %Y')}"
                    else:
                        return random.choice(data['responses'])
        
        # If no pattern matches, return a default response
        return random.choice(self.default_responses)

# Create a global chatbot instance
chatbot = SimpleChatbot()

def chat(message):
    """
    Main function to get chatbot response
    """
    return chatbot.get_response(message)

if __name__ == "__main__":
    print("ChatBot: Hello! I'm your AI assistant. Type 'quit' to exit.")
    print("-" * 50)
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("ChatBot: Goodbye! Have a great day!")
            break
        
        response = chat(user_input)
        print(f"ChatBot: {response}")
