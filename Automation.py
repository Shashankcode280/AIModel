# Import required libraries
from typing import List
from AppOpener import Close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Client = Groq(api_key=GroqAPIKey)

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.getenv('Username', 'User')}, You're a content writer. You have to write content like letter"}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = Client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)

    file_path = rf"Data/{Topic.lower().replace(' ', '_')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(file_path)
    return True

def YouTubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

def CloseApp(app):
    if "chrome" not in app:
        try:
            Close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
    }
    action = actions.get(command)
    if action:
        action()
    return True

async def TranslateAndExecute(commands: List[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            if command not in ["open it", "open file"]:
                funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        else:
            print(f"No Function Found. For {command}")
    
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: List[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
