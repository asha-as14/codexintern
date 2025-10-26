import json
import os
import webbrowser
from datetime import datetime
from speech import SpeechEngine
from weather import WeatherClient
from news import NewsClient
from utils import parse_reminder_command

CONFIG_PATH = "config.json"

class Assistant:
    def __init__(self):
        self.speech = SpeechEngine()
        self.speak = self.speech.speak
        self.listen = self.speech.listen
        self.wake_word = "assistant"
        self.config = self.load_config()
        self.weather_client = WeatherClient(self.config.get("openweather_api_key"))
        self.news_client = NewsClient(self.config.get("news_rss_url"))
        self.speak("Assistant initialized and ready.")

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def handle_command(self, text, reminder_manager=None):
        if not text:
            return

        text = text.lower().strip()
        print(f"Command: {text}")

        # Exit
        if any(kw in text for kw in ["exit", "quit", "stop assistant", "goodbye"]):
            self.speak("Goodbye. Exiting now.")
            raise KeyboardInterrupt()

        # Time
        if "time" in text:
            now = datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {now}")
            return

        # Reminders
        if text.startswith("set reminder") or text.startswith("remind me"):
            if not reminder_manager:
                self.speak("Sorry, reminders are not available right now.")
                return
            reminder = parse_reminder_command(text)
            if reminder:
                reminder_manager.add_reminder(reminder)
                self.speak(f"Reminder set: {reminder['text']} at {reminder['time'].strftime('%Y-%m-%d %I:%M %p')}")
            else:
                self.speak("I couldn't understand the reminder time. Try 'set reminder to call mom at 6 pm tomorrow'.")
            return

        # Weather
        if "weather" in text:
            # attempt to extract city
            parts = text.split("in")
            city = parts[-1].strip() if len(parts) > 1 else None
            if not city:
                city = None
            try:
                w = self.weather_client.get_weather(city)
                if w:
                    self.speak(w)
                else:
                    self.speak("Sorry, I couldn't fetch the weather.")
            except Exception as e:
                print("Weather error:", e)
                self.speak("I had trouble getting the weather.")
            return

        # News
        if "news" in text or "headlines" in text:
            try:
                headlines = self.news_client.get_headlines(limit=5)
                if headlines:
                    self.speak("Here are the top headlines.")
                    for h in headlines:
                        self.speak(h)
                else:
                    self.speak("I couldn't find news right now.")
            except Exception as e:
                print("News error:", e)
                self.speak("I ran into an error fetching news.")
            return

        # Open website
        if text.startswith("open ") or text.startswith("go to "):
            site = text.replace("open ", "").replace("go to ", "").strip()
            if not site.startswith("http"):
                if "." not in site:
                    site = "https://www." + site + ".com"
                else:
                    site = "https://" + site
            webbrowser.open(site)
            self.speak(f"Opening {site}")
            return

        # Search web
        if text.startswith("search for ") or text.startswith("search "):
            query = text.replace("search for ", "").replace("search ", "")
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            self.speak(f"Searching the web for {query}")
            return

        # Fallback
        self.speak("Sorry, I didn't understand that command. I can set reminders, tell the time, get weather, and read news.")

    def run(self, reminder_manager=None):
        self.speak("Say 'assistant' to wake me, then give a command.")
        while True:
            print("Listening for wake word...")
            text = self.listen(timeout=None, phrase_time_limit=5, wake_word=self.wake_word)
            if not text:
                continue
            # If wake word was detected, prompt for command
            # The speech.listen() function returns the full utterance; if wake word present
            if self.wake_word in text.lower():
                self.speak("Yes?")
                cmd = self.listen(timeout=6, phrase_time_limit=8)
                if cmd:
                    try:
                        self.handle_command(cmd, reminder_manager)
                    except KeyboardInterrupt:
                        raise
                else:
                    self.speak("I didn't hear anything.")
