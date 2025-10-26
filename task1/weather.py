import requests
from datetime import datetime

class WeatherClient:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_weather(self, city=None):
        if not self.api_key:
            return "Weather API key not configured in config.json."
        if not city:
            city = "New Delhi"  # fallback
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        r = requests.get(url, params=params, timeout=8)
        if r.status_code != 200:
            return None
        data = r.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels = data["main"].get("feels_like")
        humidity = data["main"].get("humidity")
        return f"Weather in {city}: {desc}. Temperature {temp}°C, feels like {feels}°C. Humidity {humidity}%."
