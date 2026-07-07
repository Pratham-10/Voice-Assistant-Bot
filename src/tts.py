import sys
import subprocess
import threading

_engine = None
_speak_lock = threading.Lock()

def _get_pyttsx3_engine():
    """Lazily initializes the pyttsx3 engine to avoid unnecessary overhead or imports."""
    global _engine
    if _engine is None:
        try:
            import pyttsx3
            _engine = pyttsx3.init()
            # Set default voice if available
            voices = _engine.getProperty('voices')
            if voices:
                _engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"Failed to initialize pyttsx3 engine: {e}")
    return _engine

def speak(audio):
    """
    Speaks the given audio text.
    - macOS: Uses the native 'say' command which is extremely fast and reliable.
    - Windows: Uses pyttsx3 (SAPI5) or falls back to win32com SAPI.
    - Linux/Others: Uses pyttsx3 (espeak).
    """
    global _speak_lock
    from src.state import set_state, State
    
    with _speak_lock:
        try:
            set_state(State.SPEAKING)
            print(f"Assistant: {audio}")
            
            if sys.platform == "darwin":
                try:
                    # Use native macOS speech synthesizer command line utility
                    # Using Popen allows us to capture KeyboardInterrupt and stop speech immediately
                    proc = subprocess.Popen(["say", audio])
                    try:
                        proc.wait()
                    except KeyboardInterrupt:
                        proc.terminate()
                        proc.wait()
                        print("\n[Speech Interrupted]")
                        raise
                    return
                except Exception as e:
                    print(f"macOS native 'say' failed: {e}")
                    
            elif sys.platform == "win32":
                engine = _get_pyttsx3_engine()
                if engine:
                    try:
                        engine.say(audio)
                        engine.runAndWait()
                        return
                    except Exception as e:
                        print(f"pyttsx3 run failed on Windows: {e}. Trying COM SAPI fallback.")
                
                # Try direct SAPI dispatch via win32com
                try:
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    speaker.Speak(audio)
                except Exception as ex:
                    print(f"Windows COM SAPI speech synthesis failed: {ex}")
                    
            else:
                # Linux or other POSIX operating system
                engine = _get_pyttsx3_engine()
                if engine:
                    try:
                        engine.say(audio)
                        engine.runAndWait()
                    except Exception as e:
                        print(f"pyttsx3 speech synthesis failed: {e}. Check if espeak is installed.")
        finally:
            set_state(State.IDLE)
