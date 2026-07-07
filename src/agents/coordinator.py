from google import genai
from google.genai import types
import pyautogui

from src.config import gemini_apikey
from src.tts import speak

# Tools imports
from src.actions import weather_updates
from src.tools.spotify_tool import play_spotify_music, control_spotify_playback
from src.tools.youtube_tool import play_on_youtube
from src.tools.google_tools import list_calendar_events, create_calendar_event, send_gmail, delete_calendar_event, reschedule_calendar_event
from src.tools.reminder_tool import create_reminder as create_local_reminder, list_reminders as list_local_reminders
from src.tools.search_tool import web_search

# Define local tool wrappers to register with Gemini
def play_music(song_name: str, artist_name: str = None) -> str:
    """
    Plays a song. Attempts to use Spotify first (requires Spotify Premium). 
    If Spotify is not configured or fails, falls back to searching and playing on YouTube in the web browser.
    
    Args:
        song_name: The name of the song or track to play.
        artist_name: Optional name of the artist.
    """
    import src.config as config
    if config.spotify_client_id:
        print("[Coordinator] Trying Spotify to play music...")
        res = play_spotify_music(song_name, artist_name)
        # If successfully initiated Spotify playback, return result
        if "Error" not in res and "not configured" not in res and "No active Spotify" not in res:
            return res
        print(f"[Coordinator] Spotify fallback triggered: {res}")
    
    print("[Coordinator] Playing on YouTube instead...")
    return play_on_youtube(song_name)

def control_music_playback(action: str) -> str:
    """
    Controls current music playback (pause, resume, skip to next, go to previous).
    
    Args:
        action: The action to perform. Allowed values: 'pause', 'resume', 'play', 'skip', 'next', 'previous', 'prev'.
    """
    import src.config as config
    if config.spotify_client_id:
        res = control_spotify_playback(action)
        if "not configured" not in res:
            return res
            
    # Fallback to local keyboard media controls using pyautogui
    action_lower = action.lower()
    try:
        if action_lower in ('pause', 'stop', 'play', 'resume'):
            pyautogui.press('playpause')
            return f"Executed system media play/pause key fallback for action '{action}'."
        elif action_lower in ('skip', 'next'):
            pyautogui.press('nexttrack')
            return f"Executed system next track key fallback for action '{action}'."
        elif action_lower in ('previous', 'prev'):
            pyautogui.press('prevtrack')
            return f"Executed system previous track key fallback for action '{action}'."
    except Exception as e:
        return f"Failed to control music playback: {e}"
    return f"Unsupported playback control action: {action}"

def search_google_calendar(max_results: int = 5) -> str:
    """
    Retrieves upcoming events from the user's Google Calendar.
    
    Args:
        max_results: Maximum number of events to list. Default is 5.
    """
    return list_calendar_events(max_results)

def create_calendar_event_tool(summary: str, start_time: str, duration_minutes: int = 30) -> str:
    """
    Creates a new calendar event in Google Calendar.
    
    Args:
        summary: Title/Summary of the meeting or event.
        start_time: ISO-8601 string of the start time (e.g. '2026-07-07T14:00:00').
        duration_minutes: Duration of the event in minutes. Default is 30.
    """
    return create_calendar_event(summary, start_time, duration_minutes)

def send_email_tool(to_email: str, subject: str, message_body: str) -> str:
    """
    Sends an email using the user's Gmail account.
    
    Args:
        to_email: The recipient's email address.
        subject: The subject of the email.
        message_body: The body content of the email.
    """
    return send_gmail(to_email, subject, message_body)

def check_weather(city: str) -> str:
    """
    Checks the current weather conditions for a specified city.
    
    Args:
        city: The name of the city (e.g., 'London', 'Mumbai').
    """
    return weather_updates(city)

def set_reminder(reminder_text: str, delay_seconds: int) -> str:
    """
    Sets a reminder to notify the user after a specific delay in seconds.
    
    Args:
        reminder_text: What the reminder is about.
        delay_seconds: Seconds to wait before reminding the user.
    """
    return create_local_reminder(reminder_text, delay_seconds)

def list_reminders_tool() -> str:
    """
    Lists all of the user's active/pending reminders.
    """
    return list_local_reminders()

def web_search_tool(query: str) -> str:
    """
    Performs a web search to find answers to questions about real-time, current events or general information.
    
    Args:
        query: The search term or question to search the web for.
    """
    return web_search(query)

def delete_calendar_event_tool(summary: str) -> str:
    """
    Deletes an event from the Google Calendar by searching for its title/summary.
    
    Args:
        summary: Title/Summary of the event to delete.
    """
    return delete_calendar_event(summary)

def reschedule_calendar_event_tool(summary: str, new_start_time: str, duration_minutes: int = 30) -> str:
    """
    Reschedules an existing event in the Google Calendar to a new start time.
    
    Args:
        summary: Title/Summary of the event to reschedule.
        new_start_time: ISO-8601 string of the new start time (e.g. '2026-07-07T15:00:00').
        duration_minutes: Duration of the rescheduled event in minutes. Default is 30.
    """
    return reschedule_calendar_event(summary, new_start_time, duration_minutes)


class CoordinatorAgent:
    """
    Main orchestrator agent that manages the Gemini Client and maps user commands
    directly to registered tool calls, eliminating hardcoded string lookups.
    """
    def __init__(self):
        # Lazily setup genai client
        if not gemini_apikey:
            raise ValueError("GEMINI_API_KEY is not configured in .env file.")
        
        self.client = genai.Client(api_key=gemini_apikey)
        
        self.tools = [
            play_music,
            control_music_playback,
            search_google_calendar,
            create_calendar_event_tool,
            delete_calendar_event_tool,
            reschedule_calendar_event_tool,
            send_email_tool,
            check_weather,
            set_reminder,
            list_reminders_tool,
            web_search_tool
        ]
        
        import datetime
        current_dt = datetime.datetime.now().strftime("%A, %B %d, %Y, %I:%M %p")
        system_instruction = (
            "You are Voice Assistant V2, a state-of-the-art agentic personal assistant. "
            "You have access to a set of local tools: playing music, controlling playback, "
            "managing Google Calendar, sending Gmail emails, setting reminders, searching the web, "
            "and checking the weather. "
            "When the user asks you to do something that can be answered or executed using a tool, "
            "always call the appropriate tool. "
            "Respond in a natural, conversational, and concise manner, as your response will be spoken aloud. "
            "Keep your final spoken answers under 2-3 sentences when possible unless detailed info is requested. "
            f"\nThe current local date and time is {current_dt}. "
            "Use this to resolve relative date expressions like 'tomorrow', 'next Monday', or 'in two hours' "
            "when calling calendar or reminder tools."
        )
        
        config = types.GenerateContentConfig(
            systemInstruction=system_instruction,
            temperature=0.7,
            tools=self.tools,
            max_output_tokens=512
        )
        
        # Create a persistent chat session
        self.chat_session = self.client.chats.create(
            model="gemini-2.5-flash",
            config=config
        )

    def process_query(self, query: str) -> str:
        """
        Sends user query to the Gemini model and automatically executes requested tool calls.
        Returns the final spoken text reply.
        """
        try:
            response = self.chat_session.send_message(query)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini Coordinator Agent Error: {e}")
            return "Sorry, I encountered an error while processing that command."
