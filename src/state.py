import threading

class State:
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"

_current_state = State.IDLE
_lock = threading.Lock()

def set_state(state: str):
    """Sets the global assistant state thread-safely."""
    global _current_state
    with _lock:
        _current_state = state

def get_state() -> str:
    """Gets the global assistant state thread-safely."""
    global _current_state
    with _lock:
        return _current_state
