import pyttsx3
import speech_recognition as sr
import os
import webbrowser
import openai
from config import apikey,weather_apikey
import datetime
import requests
import pyautogui

# engine=pyttsx3.init('sapi5')
engine=pyttsx3.init()
voices=engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)

chatStr=""

def music_controls(command):
    if 'play' in command:
        pyautogui.press('playpause')
    elif 'pause' in command:
        pyautogui.press('playpause')
    elif 'next' in command:
        pyautogui.press('nexttrack')
    elif 'previous' in command:
        pyautogui.press('prevtrack')



def weather_updates(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = weather_apikey
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    try:
        url = base_url + "appid=" + api_key + "&q=" + city
        response = requests.get(url,params=params)
        response.raise_for_status()  # Check for any errors
        weather_data = response.json()

        # Extract relevant information from the response
        temperature = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        speak(f"Weather in {city}:")
        speak(f"Temperature: {temperature} degrees Celsius")
        speak(f"Description: {description}")
        speak(f"Humidity: {humidity}%")
        speak(f"Wind Speed: {wind_speed} meters per second")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def wishGreeting():
    hour=int(datetime.datetime.now().hour)
    if hour>=5 and hour<12:
        speak("Good Morning!")
    elif hour>=12 and hour<17:
        speak("Good Afternoon!")
    elif hour>=17 and hour<20:
        speak("Good Evening!")
    elif hour>=0 and hour<5:
        speak("Good Night!")

def chat(query):
    global chatStr
    print(chatStr)
    openai.api_key = apikey
    chatStr += f"Pratham: {query}\n : "
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=chatStr,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    try:
        speak(response["choices"][0]["text"])
        chatStr += f"{response['choices'][0]['text']}\n"
        return response["choices"][0]["text"]
    except Exception as e:
        print(f"Error occurred: {e}")
        return "An error occurred while processing the response."


def ai(prompt):
    openai.api_key = apikey
    text = f"OpenAI response for Prompt: {prompt} \n *************************\n\n"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    text += response["choices"][0]["text"]
    if not os.path.exists("Openai"):
        os.mkdir("Openai")

    with open(f"Openai/{''.join(prompt.split('intelligence')[1:]).strip() }.txt", "w") as f:
        f.write(text)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()
# def speak(text):
#     os.system(f"say{text}")

def takeCommand():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1
        audio=r.listen(source)
    try:
        print("Recognizing....")
        query=r.recognize_google(audio, language='en-in')
        print(f"User said:{query}\n")

    except Exception as e:
        print("Say that again please....")
        return "None"
    return query

if __name__ == '__main__':
    wishGreeting()
    speak("Hello I am your voice assistant")
    while True:
        query=takeCommand().lower()
        sites = [["youtube","https://www.youtube.com"],["google","https://www.google.com"],["stackoverflow","https://www.stackoverflow.com"],["geeksforgeeks","https://"]]
        cities = ["Ahmedabad","Mumbai","Banglore","Delhi","Chennai","Jaipur"]
        for site in sites:
            if f"Open {site[0]}".lower() in query.lower():
                speak(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])
        # for city in cities:
        #     if city.lower() in query.lower():
        #         weather_updates(city)

        if "open music" in query:
            musicPath = r"C:\Users\Admin\Downloads\Baby-Calm-Down.mp3"
            os.startfile(musicPath)
            while True:
                command = takeCommand().lower()

                if 'stop' in command or 'quit' in command:
                    # Stop music playback
                    break

                # Perform music controls based on voice commands
                music_controls(command)

        elif 'time' in query:
            currTime=datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {currTime}")

        elif "Using artificial intelligence".lower() in query.lower():
            ai(prompt=query)

        elif "Quit".lower() in query.lower():
            exit()

        elif "weather".lower() in query.lower():
            for city in cities:
                if city.lower() in query.lower():
                    weather_updates(city)

        elif "enable chatting".lower() in query.lower():
            while True:
                query=takeCommand().lower()
                print("Chatting...")
                chat(query)
                if "Quit chatting".lower() in query.lower():
                    break


