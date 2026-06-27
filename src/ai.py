import os
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
from src.config import gemini_apikey
from src.tts import speak

# Global client and chat session references
_client = None
_chat_session = None

def get_gemini_client():
    """Lazily instantiates the Gemini client using the configured API key."""
    global _client
    if _client is None:
        if not gemini_apikey:
            return None
        try:
            _client = genai.Client(api_key=gemini_apikey)
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            return None
    return _client

def get_chat_session():
    """Lazily creates and returns a persistent Gemini chat session with system instructions."""
    global _chat_session
    client = get_gemini_client()
    if not client:
        return None
        
    if _chat_session is None:
        try:
            config = types.GenerateContentConfig(
                systemInstruction="You are a helpful and concise voice assistant.",
                temperature=0.7,
                max_output_tokens=256
            )
            # Create a persistent chat session using gemini-2.5-flash
            _chat_session = client.chats.create(
                model="gemini-2.5-flash",
                config=config
            )
        except Exception as e:
            print(f"Error creating Gemini chat session: {e}")
            return None
    return _chat_session

def chat(query):
    """
    Sends the user query to the persistent Gemini chat session.
    Speaks the assistant's reply and returns it.
    """
    chat_session = get_chat_session()
    if not chat_session:
        speak("Gemini API key is not configured. Please set GEMINI_API_KEY in the .env file.")
        return "API key missing"

    try:
        response = chat_session.send_message(query)
        reply = response.text.strip()
        speak(reply)
        return reply
    except Exception as e:
        print(f"Gemini Chat API error: {e}")
        speak("Sorry, I encountered an error while communicating with Gemini.")
        return "Error occurred"

def ai(prompt):
    """
    Calls Gemini to generate a text file containing the response for the prompt.
    Saves the file to 'Openai/' directory (kept named 'Openai' to retain original folder functionality).
    """
    client = get_gemini_client()
    if not client:
        speak("Gemini API key is not configured. Please set GEMINI_API_KEY in the .env file.")
        return

    speak("Processing request with Gemini AI, please wait...")
    
    try:
        config = types.GenerateContentConfig(
            systemInstruction="You are a software developer assistant. Generate complete, detailed, and clean code or answers.",
            temperature=0.7,
            max_output_tokens=1000
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        reply = response.text.strip()
    except Exception as e:
        print(f"Gemini Generation API error: {e}")
        speak("Failed to generate AI response.")
        return

    # Extract filename from query using original split logic on word 'intelligence'
    filename_part = "".join(prompt.split('intelligence')[1:]).strip()
    
    # Sanitize filename (remove characters that could violate file system path rules)
    filename = "".join(c for c in filename_part if c.isalnum() or c in (' ', '_', '-')).strip()
    if not filename:
        filename = "ai_response"

    # Ensure output directory exists (we keep the directory name 'Openai' as requested by "keeping the functionalities")
    if not os.path.exists("Openai"):
        os.mkdir("Openai")

    filepath = f"Openai/{filename}.txt"
    text_content = f"Gemini response for Prompt: {prompt} \n *************************\n\n{reply}"
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text_content)
        speak(f"AI response saved successfully as {filename}.txt")
    except Exception as e:
        print(f"Failed to write file {filepath}: {e}")
        speak("I generated the response but failed to save it to a file.")
