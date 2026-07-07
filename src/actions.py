import os
import sys
import subprocess
import requests
from src.config import weather_apikey
from src.tts import speak

def weather_updates(city: str) -> str:
    """
    Fetches the weather updates for a specified city from OpenWeatherMap.
    Returns the weather information as a formatted string.
    """
    if not weather_apikey:
        return "Weather API key is not configured. Please set WEATHER_API_KEY in your .env file."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": weather_apikey,
        "units": "metric"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        temperature = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]

        weather_info = (
            f"Weather in {city}:\n"
            f"- Temperature: {temperature}°C\n"
            f"- Conditions: {description}\n"
            f"- Humidity: {humidity}%\n"
            f"- Wind Speed: {wind_speed} m/s"
        )
        return weather_info

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return f"Failed to fetch weather for {city}. Please check the city name or API key."
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return f"An error occurred while getting the weather updates for {city}."

def music_controls(command):
    """
    Simulates media keys on the keyboard using pyautogui to control active media players.
    """
    try:
        import pyautogui
        if 'play' in command or 'pause' in command:
            pyautogui.press('playpause')
        elif 'next' in command:
            pyautogui.press('nexttrack')
        elif 'previous' in command:
            pyautogui.press('prevtrack')
    except Exception as e:
        print(f"Error executing music command '{command}' via pyautogui: {e}")
        print("Note: On macOS, this terminal/editor might require Accessibility permissions in System Settings.")

def play_audio_file(file_path):
    """
    Plays a local audio file cross-platform using the default system media player.
    """
    if not file_path:
        speak("Music path is not set. Please set the MUSIC_PATH in your .env file.")
        return False

    expanded_path = os.path.expanduser(file_path)
    if not os.path.exists(expanded_path):
        speak(f"Music file not found at {expanded_path}")
        return False

    try:
        speak(f"Playing music...")
        if sys.platform == "win32":
            os.startfile(expanded_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", expanded_path], check=True)
        else:
            subprocess.run(["xdg-open", expanded_path], check=True)
        return True
    except Exception as e:
        print(f"Failed to play music file: {e}")
        speak("Could not start playing the music file.")
        return False
