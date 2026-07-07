import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# API Keys and application configurations
gemini_apikey = os.getenv("GEMINI_API_KEY", "")
# Backwards compatibility export
apikey = gemini_apikey
weather_apikey = os.getenv("WEATHER_API_KEY", "")
music_path = os.getenv("MUSIC_PATH", "")

# Spotify Web API Configurations
spotify_client_id = os.getenv("SPOTIPY_CLIENT_ID", "")
spotify_client_secret = os.getenv("SPOTIPY_CLIENT_SECRET", "")
spotify_redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")

# Google API Credentials Configurations
google_credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

