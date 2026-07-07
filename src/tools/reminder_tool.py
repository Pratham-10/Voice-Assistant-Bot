import time
import sqlite3
import threading
from datetime import datetime, timedelta
from src.tts import speak

DB_PATH = "reminders.db"

def init_db():
    """Initializes the SQLite reminders database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            due_time TIMESTAMP NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# Initialize on import
init_db()

def create_reminder(reminder_text: str, delay_seconds: int) -> str:
    """
    Creates a reminder to trigger after a specific delay.
    
    Args:
        reminder_text: The description of what to remind the user about.
        delay_seconds: The delay in seconds before the reminder triggers.
        
    Returns:
        Confirmation message.
    """
    due = datetime.now() + timedelta(seconds=delay_seconds)
    due_str = due.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (text, due_time) VALUES (?, ?)",
            (reminder_text, due_str)
        )
        conn.commit()
        conn.close()
        
        minutes = delay_seconds // 60
        seconds = delay_seconds % 60
        time_msg = ""
        if minutes > 0:
            time_msg += f"{minutes} minute(s) "
        if seconds > 0 or minutes == 0:
            time_msg += f"{seconds} second(s)"
            
        return f"Got it. I'll remind you to '{reminder_text}' in {time_msg.strip()}."
    except Exception as e:
        print(f"Error creating reminder: {e}")
        return f"Failed to create reminder: {e}"

def list_reminders() -> str:
    """
    Lists all pending/active reminders.
    
    Returns:
        A list of active reminders or a status message.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text, due_time FROM reminders WHERE completed = 0 ORDER BY due_time ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "You have no active reminders."
            
        summary = "Here are your active reminders:\n"
        for row in rows:
            summary += f"- '{row[0]}' due at {row[1]}\n"
        return summary
    except Exception as e:
        print(f"Error listing reminders: {e}")
        return "Failed to list reminders."

def check_reminders_loop():
    """Background loop checking for and triggering due reminders."""
    while True:
        try:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Find reminders that are due and not completed
            cursor.execute(
                "SELECT id, text FROM reminders WHERE due_time <= ? AND completed = 0",
                (now_str,)
            )
            due_reminders = cursor.fetchall()
            
            for rid, text in due_reminders:
                # Mark as completed
                cursor.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (rid,))
                conn.commit()
                
                # Check current assistant state
                from src.state import get_state, State
                import sys
                import subprocess
                
                current_state = get_state()
                if current_state == State.IDLE:
                    # Speak reminder when the assistant is completely idle
                    speak(f"Reminder: Please remember to {text}")
                else:
                    # Print in terminal and show a macOS notification to prevent audio collision
                    print(f"\n[Visual Reminder] Please remember to {text}\n")
                    if sys.platform == "darwin":
                        escaped_text = text.replace('"', '\\"')
                        subprocess.run([
                            "osascript", 
                            "-e", 
                            f'display notification "Please remember to {escaped_text}" with title "Voice Assistant Reminder"'
                        ], capture_output=True)
                
            conn.close()
        except Exception as e:
            print(f"Error in background reminders loop: {e}")
            
        time.sleep(1)

# Start background checking thread
bg_thread = threading.Thread(target=check_reminders_loop, daemon=True)
bg_thread.start()
