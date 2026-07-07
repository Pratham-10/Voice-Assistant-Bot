import datetime
import sys
from src.tts import speak
from src.stt import takeCommand
from src.agents.coordinator import CoordinatorAgent

def wishGreeting():
    """Greets the user based on the current hour of the day."""
    hour = int(datetime.datetime.now().hour)
    if 5 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 17:
        speak("Good Afternoon!")
    elif 17 <= hour < 21:
        speak("Good Evening!")
    else:
        speak("Good Night!")

def main():
    """Main loop for the Voice Assistant Bot V2."""
    wishGreeting()
    speak("Voice Assistant V2 is ready.")
    
    # Initialize the Gemini Coordinator Agent
    try:
        agent = CoordinatorAgent()
    except ValueError as ve:
        speak(str(ve))
        sys.exit(1)
    except Exception as e:
        speak("Failed to initialize Gemini coordinator agent. Please check your API key and connection.")
        print(f"Initialization Error: {e}")
        sys.exit(1)
        
    speak("How can I help you today?")
    
    while True:
        try:
            query = takeCommand().strip()
            if not query or query.lower() == "none":
                continue
                
            # Direct quit check
            if query.lower() in ("quit", "exit", "goodbye", "bye"):
                speak("Goodbye! Have a great day.")
                sys.exit(0)
                
            print(f"Processing query: '{query}'")
            # Process query using coordinator agent (handles Gemini, routing, and tools execution)
            from src.state import set_state, State
            try:
                set_state(State.THINKING)
                response = agent.process_query(query)
            finally:
                set_state(State.IDLE)
            
            # Speak the final agent response
            speak(response)
            
        except KeyboardInterrupt:
            # Let KeyboardInterrupt stop ongoing speech or exit chat cleanly
            print("\n[Session interrupted by user]")
            speak("Stopped.")
        except Exception as e:
            print(f"Error in main loop: {e}")
            speak("An unexpected error occurred.")

if __name__ == '__main__':
    main()
