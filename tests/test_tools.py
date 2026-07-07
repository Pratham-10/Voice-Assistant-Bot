import unittest
from unittest.mock import patch, MagicMock
import os

# Make sure src can be imported
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import config to patch it directly
import src.config as config

from src.agents.coordinator import play_music, control_music_playback
from src.tools.reminder_tool import create_reminder
from src.tools.search_tool import web_search

class TestVoiceAssistantV2Tools(unittest.TestCase):
    
    @patch('src.agents.coordinator.play_spotify_music')
    @patch('src.agents.coordinator.play_on_youtube')
    def test_play_music_spotify_success(self, mock_youtube, mock_spotify):
        # Set config mock
        with patch.object(config, 'spotify_client_id', 'mock_client_id'):
            mock_spotify.return_value = "Playing 'Song' on Spotify."
            
            result = play_music("Song")
            
            self.assertEqual(result, "Playing 'Song' on Spotify.")
            mock_spotify.assert_called_once_with("Song", None)
            mock_youtube.assert_not_called()

    @patch('src.agents.coordinator.play_spotify_music')
    @patch('src.agents.coordinator.play_on_youtube')
    def test_play_music_spotify_fails_fallback(self, mock_youtube, mock_spotify):
        # Set config mock
        with patch.object(config, 'spotify_client_id', 'mock_client_id'):
            mock_spotify.return_value = "Spotify Playback Error: No active Spotify device"
            mock_youtube.return_value = "Opening 'Song' on YouTube in browser."
            
            result = play_music("Song")
            
            self.assertEqual(result, "Opening 'Song' on YouTube in browser.")
            mock_spotify.assert_called_once_with("Song", None)
            mock_youtube.assert_called_once_with("Song")

    @patch('src.agents.coordinator.control_spotify_playback')
    @patch('pyautogui.press')
    def test_control_music_spotify(self, mock_pyautogui, mock_spotify):
        # Controls Spotify if client_id is set
        with patch.object(config, 'spotify_client_id', 'mock_client_id'):
            mock_spotify.return_value = "Paused Spotify playback."
            
            result = control_music_playback("pause")
            
            self.assertEqual(result, "Paused Spotify playback.")
            mock_spotify.assert_called_once_with("pause")
            mock_pyautogui.assert_not_called()

    @patch('src.agents.coordinator.control_spotify_playback')
    @patch('pyautogui.press')
    def test_control_music_pyautogui_fallback(self, mock_pyautogui, mock_spotify):
        # Falls back to pyautogui media keys if Spotify is not configured
        with patch.object(config, 'spotify_client_id', ''):
            result = control_music_playback("pause")
            
            self.assertIn("Executed system media play/pause key fallback", result)
            mock_spotify.assert_not_called()
            mock_pyautogui.assert_called_once_with('playpause')

    @patch('src.tools.reminder_tool.sqlite3.connect')
    def test_reminder_creation(self, mock_connect):
        # Mocks sqlite insertion
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        result = create_reminder("Buy milk", 60)
        self.assertIn("Buy milk", result)
        self.assertIn("1 minute(s)", result)

    @patch('src.tools.search_tool.DDGS')
    def test_web_search_mocked(self, mock_ddgs):
        # Mock DuckDuckGo text search
        mock_instance = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_instance
        mock_instance.text.return_value = [
            {'title': 'Test Title', 'body': 'Test Body', 'href': 'http://test.com'}
        ]
        
        result = web_search("What is python?")
        self.assertIn("Test Title", result)
        self.assertIn("Test Body", result)
        self.assertIn("http://test.com", result)

    @patch('src.tools.youtube_tool.DDGS')
    @patch('webbrowser.open')
    def test_youtube_tool_mocked(self, mock_webopen, mock_ddgs):
        # Mock DuckDuckGo video search
        mock_instance = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_instance
        mock_instance.videos.return_value = [
            {'title': 'Song Video', 'content': 'https://youtube.com/watch?v=123'}
        ]
        
        from src.tools.youtube_tool import play_on_youtube
        result = play_on_youtube("My Song")
        
        self.assertIn("Found and opening 'Song Video' on YouTube", result)
        mock_webopen.assert_called_once_with('https://youtube.com/watch?v=123')

    @patch('src.tools.google_tools.get_google_credentials')
    @patch('src.tools.google_tools.build')
    def test_delete_calendar_event_mocked(self, mock_build, mock_creds):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        # Mock search list
        mock_service.events().list().execute.return_value = {
            'items': [{'id': 'evt123', 'summary': 'Code Review', 'start': {'dateTime': '2026-07-08T16:00:00'}}]
        }
        
        from src.tools.google_tools import delete_calendar_event
        result = delete_calendar_event("Code Review")
        
        self.assertIn("Successfully deleted the event 'Code Review'", result)
        mock_service.events().delete.assert_called_once_with(calendarId='primary', eventId='evt123')

    @patch('src.tools.google_tools.get_google_credentials')
    @patch('src.tools.google_tools.build')
    def test_reschedule_calendar_event_mocked(self, mock_build, mock_creds):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        # Mock search list
        mock_service.events().list().execute.return_value = {
            'items': [{'id': 'evt123', 'summary': 'Code Review'}]
        }
        # Mock get calendar info for timezone
        mock_service.calendars().get().execute.return_value = {'timeZone': 'Asia/Kolkata'}
        
        from src.tools.google_tools import reschedule_calendar_event
        result = reschedule_calendar_event("Code Review", "2026-07-08T17:00:00", 30)
        
        self.assertIn("Successfully rescheduled 'Code Review' to 2026-07-08T17:00:00", result)
        mock_service.events().update.assert_called_once()

if __name__ == '__main__':
    unittest.main()
