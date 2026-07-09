from datetime import datetime
import time
import requests
import os

device_name = "🐾 Bobcat Desk Clock"
city = "San Marcos"


def get_weather_icon(weather_desc):
    weather_desc = weather_desc.lower()

    if "sun" in weather_desc or "clear" in weather_desc:
        return "☀"
    elif "cloud" in weather_desc or "overcast" in weather_desc:
        return "☁"
    elif "rain" in weather_desc or "drizzle" in weather_desc:
        return "🌧"
    elif "thunder" in weather_desc or "storm" in weather_desc:
        return "⚡"
    elif "snow" in weather_desc or "ice" in weather_desc:
        return "❄"
    elif "fog" in weather_desc or "mist" in weather_desc:
        return "🌫"
    else:
        return "?"


def get_weather(city):
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=j1"

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        temp_f = data["current_condition"][0]["temp_F"]
        weather_desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        today_hourly = data["weather"][0]["hourly"]

        return temp_f, weather_desc, today_hourly

    except Exception:
        return "--", "Unavailable", []


cached_temp_f = "--"
cached_weather_desc = "Unavailable"
cached_hourly = []

last_weather_update = 0
weather_refresh_seconds = 600 

def clear_screen():
    print("\033c", end="")


while True:
    current_time = datetime.now()

    formatted_time = current_time.strftime("%-I:%M %p")
    formatted_date = current_time.strftime("%A, %b %d")

    current_timestamp = time.time()


    if current_timestamp - last_weather_update >= weather_refresh_seconds:
        cached_temp_f, cached_weather_desc, cached_hourly = get_weather(city)

        print("Refreshing weather...")

        last_weather_update = current_timestamp

    temp_f = cached_temp_f
    weather_desc = cached_weather_desc
    today_hourly = cached_hourly

    icon = get_weather_icon(weather_desc)

    current_hour = current_time.hour
    next_rain_chance = 0

    for hour in today_hourly:
        forecast_time = int(hour["time"]) // 100

        if forecast_time >= current_hour:
            next_rain_chance = int(hour["chanceofrain"])
            break

    clear_screen()
    print(device_name)
    print(city)
    print()
    print(formatted_time)
    print(formatted_date)
    print()
    print(f"{temp_f}°F")
    print(f"{icon} {weather_desc}")

    if next_rain_chance >= 20:
        print(f"🌧 Rain Chance: {next_rain_chance}%")

    if "thunder" in weather_desc.lower():
        print("⚠ Storms Possible")

    seconds_until_next_minute = (60 - current_time.second - current_time.microsecond / 1_000_000)

    time.sleep(seconds_until_next_minute)