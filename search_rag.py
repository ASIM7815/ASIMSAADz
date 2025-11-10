from ddgs import DDGS
import re

class DuckDuckGoSearch:
    def __init__(self):
        """Search DuckDuckGo using official library - most reliable method"""
        self.ddgs = DDGS()
        print("[OK] DuckDuckGo Search initialized with official library!") 
    
    def search(self, query):
        """Search DuckDuckGo and return results"""
        try:
            print(f"[SEARCHING] {query}")
            # Use text search with official library
            results = []
            search_results = self.ddgs.text(query, max_results=5)
            
            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'link': result.get('href', '')
                })
            
            print(f"[OK] Found {len(results)} results")
            return results
        
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []
    
    def clean_text(self, text):
        """Remove reference numbers like [1], [2], [3] and letters like [a], [b], [c] from text"""
        if not text:
            return ""
        # Remove all patterns like [1], [2], [3], etc.
        cleaned = re.sub(r'\[\d+\]', '', text)
        # Remove all patterns like [a], [b], [c], [d], etc.
        cleaned = re.sub(r'\[([a-zA-Z])\]', '', cleaned)
        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()
    
    def format_results(self, results):
        """Format search results into a readable response"""
        if not results:
            return None
        
        # Clean the snippets and format them
        answer = ""
        for result in results[:3]:
            cleaned_snippet = self.clean_text(result.get('snippet', ''))
            if cleaned_snippet:
                answer += f"{cleaned_snippet}\n\n"
        
        return answer.strip() if answer.strip() else None
    
    def chat(self, question):
        """Answer questions using DuckDuckGo search"""
        print(f"[CHAT] User asked: {question}")
        
        # Check for greetings
        question_lower = question.lower().strip()
        
        if any(greeting in question_lower for greeting in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return "Hey there! 😊 It's great to see you! I'm here and ready to chat about anything you're curious about. What's on your mind today?"
        elif any(phrase in question_lower for phrase in ['how are you', 'how are u', 'hows it going', 'whats up']):
            return "I'm doing wonderfully, thank you for asking! 🌟 I'm excited to help you learn about whatever interests you. What would you like to know?"
        elif any(word in question_lower for word in ['thank', 'thanks', 'thx']):
            return "You're so welcome! 😊 I'm happy I could help. Feel free to ask me anything else!"
        elif any(word in question_lower for word in ['bye', 'goodbye', 'see you', 'gotta go']):
            return "It was lovely chatting with you! 💙 Take care and come back anytime!"
        
        # For knowledge questions, search the internet
        try:
            results = self.search(question)
            
            if not results:
                return "I searched for that information but couldn't find relevant results right now. 🤔\n\nTry:\n- Rephrasing your question in different words\n- Being more specific or more general\n- Asking about something else\n\nI'm here to help! 😊"
            
            # Format and return the search results
            formatted_answer = self.format_results(results)
            
            if not formatted_answer:
                return "I found some results but couldn't extract clear information. Could you try rephrasing your question? 🤔"
            
            return formatted_answer
            
        except Exception as e:
            print(f"[ERROR] Chat error: {e}")
            return f"Oops! Something went wrong while searching. 😅\n\nPlease try again or rephrase your question!"

# Create global instance
ddg_search = DuckDuckGoSearch()

def search_chat(message):
    """Main function to handle search chat"""
    return ddg_search.chat(message)

if __name__ == "__main__":
    # Test the search
    print("\n" + "="*60)
    print("Testing DuckDuckGo Search...")
    print("="*60 + "\n")
    
    test_query = "What is Python programming?"
    result = search_chat(test_query)
    print(f"Q: {test_query}")
    print(f"A: {result}")
