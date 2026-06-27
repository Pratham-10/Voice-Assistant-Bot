import datetime
import webbrowser
import sys
from src.tts import speak
from src.stt import takeCommand
from src.actions import weather_updates, music_controls, play_audio_file
from src.ai import chat, ai
from src.config import music_path

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
    """Main loop for the Voice Assistant Bot."""
    wishGreeting()
    speak("Hello, I am your voice assistant.")
    
    # Pre-configured command options
    sites = [
        ["youtube", "https://www.youtube.com"],
        ["google", "https://www.google.com"],
        ["stackoverflow", "https://www.stackoverflow.com"],
        ["geeksforgeeks", "https://www.geeksforgeeks.org"]
    ]
    cities = ["Ahmedabad", "Mumbai", "Banglore", "Delhi", "Chennai", "Jaipur"]
    
    while True:
        query = takeCommand().lower()
        if not query or query == "none":
            continue
            
        # 1. Open Websites
        site_opened = False
        for site in sites:
            if f"open {site[0]}" in query:
                speak(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])
                site_opened = True
                break
        if site_opened:
            continue
                
        # 2. Play Local Music & Control Playback
        if "open music" in query:
            path_to_play = music_path if music_path else "~/Downloads/Baby-Calm-Down.mp3"
            success = play_audio_file(path_to_play)
            if success:
                speak("Playback started. You can say 'pause', 'play', 'next', 'previous' to control media, or say 'stop' to return.")
                while True:
                    command = takeCommand().lower()
                    if 'stop' in command or 'quit' in command:
                        speak("Returning to main assistant loop.")
                        break
                    music_controls(command)
                    
        # 3. Inform Time
        elif 'time' in query:
            currTime = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"Sir, the time is {currTime}")
            
        # 4. Generate Content with AI (Trigger: "using artificial intelligence")
        elif "using artificial intelligence" in query:
            ai(prompt=query)
            
        # 5. Chat Mode (Trigger: "enable chatting")
        elif "enable chatting" in query:
            speak("Chatting enabled. Say 'quit chatting' to exit chat mode.")
            while True:
                chat_query = takeCommand().lower()
                if not chat_query or chat_query == "none":
                    continue
                if "quit chatting" in chat_query:
                    speak("Exiting chat mode.")
                    break
                print("Chatting...")
                chat(chat_query)
                
        # 6. Weather Forecasts
        elif "weather" in query:
            found_city = False
            for city in cities:
                if city.lower() in query:
                    weather_updates(city)
                    found_city = True
                    break
            if not found_city:
                speak("Which city's weather would you like to check?")
                city_query = takeCommand()
                if city_query and city_query != "None":
                    weather_updates(city_query)
                    
        # 7. Quit Application
        elif "quit" in query or "exit" in query:
            speak("Goodbye, sir. Have a great day!")
            sys.exit()

        # 8. General AI Chat Fallback
        else:
            chat(query)

if __name__ == '__main__':
    main()
