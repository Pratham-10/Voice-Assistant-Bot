import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.config import spotify_client_id, spotify_client_secret, spotify_redirect_uri

# Spotify scopes for controlling playback
SCOPE = "user-modify-playback-state user-read-playback-state"

def get_spotify_client():
    """
    Initializes and returns a Spotipy client using OAuth.
    Returns None if Spotify credentials are not set.
    """
    if not spotify_client_id or not spotify_client_secret:
        print("\n[Spotify API Info] Spotify credentials are not configured.")
        print("To use Spotify, set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in your .env file.")
        return None
    
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_uri,
            scope=SCOPE,
            open_browser=True
        ))
        return sp
    except Exception as e:
        print(f"Error initializing Spotipy: {e}")
        return None

def play_spotify_music(track_name: str, artist_name: str = None) -> str:
    """
    Searches for a track on Spotify and starts playing it.
    
    Args:
        track_name: The name of the song to search and play.
        artist_name: Optional name of the artist to filter by.
        
    Returns:
        Status message about playback status.
    """
    sp = get_spotify_client()
    if not sp:
        return "Spotify integration is not configured. Please set credentials in your .env file."

    # Construct search query
    query = track_name
    if artist_name:
        query += f" artist:{artist_name}"

    try:
        results = sp.search(q=query, limit=1, type='track')
        tracks = results.get('tracks', {}).get('items', [])
        
        if not tracks:
            return f"Could not find any song named '{track_name}' on Spotify."
            
        track = tracks[0]
        track_uri = track['uri']
        track_title = track['name']
        track_artist = track['artists'][0]['name']

        # Attempt to play on an active device
        try:
            sp.start_playback(uris=[track_uri])
            return f"Playing '{track_title}' by {track_artist} on Spotify."
        except spotipy.exceptions.SpotifyException as se:
            # Handle "No active device" error (HTTP 404)
            if se.http_status == 404:
                # Try to find any available device to start playback
                devices = sp.devices().get('devices', [])
                if devices:
                    device_id = devices[0]['id']
                    device_name = devices[0]['name']
                    try:
                        sp.start_playback(device_id=device_id, uris=[track_uri])
                        return f"Playing '{track_title}' by {track_artist} on device '{device_name}'."
                    except Exception:
                        return f"Found Spotify device '{device_name}', but failed to start playback. Please open Spotify."
                else:
                    return "No active Spotify devices found. Please open Spotify on your device and try again."
            else:
                return f"Spotify Playback Error: {se.msg}"
    except Exception as e:
        print(f"Spotify Search/Play error: {e}")
        return f"Failed to play music on Spotify: {e}"

def control_spotify_playback(action: str) -> str:
    """
    Controls Spotify playback state.
    
    Args:
        action: One of 'pause', 'resume' (or 'play'), 'skip' (or 'next'), 'previous' (or 'prev').
        
    Returns:
        Confirmation or error message.
    """
    sp = get_spotify_client()
    if not sp:
        return "Spotify is not configured."

    action_lower = action.lower()
    try:
        if action_lower in ('pause', 'stop'):
            sp.pause_playback()
            return "Paused Spotify playback."
        elif action_lower in ('resume', 'play'):
            sp.start_playback()
            return "Resumed Spotify playback."
        elif action_lower in ('skip', 'next'):
            sp.next_track()
            return "Skipped to next track on Spotify."
        elif action_lower in ('previous', 'prev'):
            sp.previous_track()
            return "Skipped to previous track on Spotify."
        else:
            return f"Unknown Spotify action: '{action}'."
    except spotipy.exceptions.SpotifyException as se:
        if se.http_status == 404:
            return "No active Spotify session/device found to control playback."
        return f"Spotify control failed: {se.msg}"
    except Exception as e:
        return f"Failed to control Spotify: {e}"
