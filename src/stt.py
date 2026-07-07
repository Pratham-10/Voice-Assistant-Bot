import speech_recognition as sr
from src.tts import speak

def takeCommand():
    """
    Listens to the user's voice command via the microphone.
    If PyAudio is missing, or microphone access fails, falls back to text-based terminal input.
    """
    try:
        import pyaudio
    except ImportError:
        print("\n[STT Info] PyAudio is not installed. Microphone input is unavailable.")
        print("To enable voice input, please install PyAudio. (macOS: 'brew install portaudio && pip install pyaudio')")
        query = input("User (keyboard fallback): ")
        return query if query.strip() else "None"

    r = sr.Recognizer()
    r.pause_threshold = 2.0
    r.non_speaking_duration = 1.0
    r.dynamic_energy_threshold = True
    
    from src.state import set_state, State
    
    try:
        with sr.Microphone() as source:
            print("Listening...")
            set_state(State.LISTENING)
            # Adjust for ambient noise briefly to improve recognition
            r.adjust_for_ambient_noise(source, duration=1.0)
            # Listen with timeouts to prevent hanging indefinitely
            audio = r.listen(source, timeout=8, phrase_time_limit=15)
    except sr.WaitTimeoutError:
        print("Listening timed out. No speech detected.")
        return "None"
    except Exception as e:
        print(f"\n[STT Info] Microphone access failed: {e}")
        query = input("User (keyboard fallback): ")
        return query if query.strip() else "None"
    finally:
        set_state(State.IDLE)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except sr.UnknownValueError:
        print("Could not understand the audio. Say that again please...")
        return "None"
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return "None"
    except Exception as e:
        print(f"Error during recognition: {e}")
        return "None"
        
    return query
