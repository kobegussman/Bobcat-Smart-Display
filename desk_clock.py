from datetime import datetime
import time
import requests

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
        # ----------------
        # GET CITY COORDINATES
        # ----------------

        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"

        geocode_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geocode_response = requests.get(
            geocode_url,
            params=geocode_params,
            timeout=10
        )

        geocode_response.raise_for_status()

        geocode_data = geocode_response.json()

        if not geocode_data.get("results"):
            raise Exception("City not found")

        location = geocode_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        # ----------------
        # GET WEATHER
        # ----------------

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "surface_pressure,"
                "wind_speed_10m,"
                "wind_direction_10m,"
            ),
            "hourly": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation_probability,"
                "weather_code,"
                "visibility"
            ),
            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max,"
                "sunrise,"
                "sunset,"
                "uv_index_max"
            ),
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "auto",
            "forecast_days": 7
        }

        response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # ----------------
        # WEATHER CODE
        # ----------------

        def weather_description(code):

            descriptions = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Drizzle",
                55: "Heavy drizzle",
                61: "Light rain",
                63: "Rain",
                65: "Heavy rain",
                71: "Light snow",
                73: "Snow",
                75: "Heavy snow",
                77: "Snow grains",
                80: "Light rain showers",
                81: "Rain showers",
                82: "Heavy rain showers",
                85: "Light snow showers",
                86: "Heavy snow showers",
                95: "Thunderstorm",
                96: "Thunderstorm with hail",
                99: "Thunderstorm with heavy hail"
            }

            return descriptions.get(
                code,
                "Unknown"
            )

        # ----------------
        # CURRENT WEATHER
        # ----------------

        current = data["current"]
        current_code = current["weather_code"]

        hourly = data["hourly"]
        current_hour_index = 0

        for i, timestamp in enumerate(hourly["time"]):
            if timestamp[:13] == current["time"][:13]:
                current_hour_index = i
                break

        current_weather = {
                    
            "temp_f": round(current["temperature_2m"]),
            "feels_like_f": round(current["apparent_temperature"]),
            "description": weather_description(current_code),
            "humidity": current["relative_humidity_2m"],
            "wind_speed": round(current["wind_speed_10m"]),
            "wind_direction": round(current["wind_direction_10m"]),
            "visibility": round(
                hourly["visibility"][current_hour_index] / 1609.34,
                1
            ),
            "uv_index": data["daily"]["uv_index_max"][0],
            "pressure": round(
                current["surface_pressure"] * 0.0295299,
                2
            )
        }
        # ----------------
        # HOURLY FORECAST
        # ----------------
        today_hourly = []

        for i in range(len(hourly["time"])):

            timestamp = hourly["time"][i]

            hour = int(timestamp[11:13])

            today_hourly.append({
                "time": hour * 100,
                "tempF": round(
                    hourly["temperature_2m"][i]
                ),
                "chanceofrain": hourly[
                    "precipitation_probability"
                ][i],
                "weatherDesc": [
                    {
                        "value": weather_description(
                            hourly["weather_code"][i]
                        )
                    }
                ]
            })

        # ----------------
        # 7-DAY FORECAST
        # ----------------

        daily = data["daily"]

        forecast = []

        for i in range(len(daily["time"])):

            description = weather_description(
                daily["weather_code"][i]
            )

            sunrise = datetime.fromisoformat(
                daily["sunrise"][i]
            ).strftime("%I:%M %p").lstrip("0")

            sunset = datetime.fromisoformat(
                daily["sunset"][i]
            ).strftime("%I:%M %p").lstrip("0")

            forecast.append({
                "date": daily["time"][i],
                "max_temp_f": round(
                    daily["temperature_2m_max"][i]
                ),
                "min_temp_f": round(
                    daily["temperature_2m_min"][i]
                ),
                "description": description,
                "rain_chance": daily[
                    "precipitation_probability_max"
                ][i],
                "sunrise": sunrise,
                "sunset": sunset
            })

        print("DEBUG CURRENT WEATHER:", current_weather)
        return (
            current_weather,
            today_hourly,
            forecast
        )

    except Exception as error:

        print("Weather error:", error)
        

        return (
            {
                "temp_f": "--",
                "feels_like_f": "--",
                "description": "Unavailable",
                "humidity": "--",
                "wind_speed": "--",
                "wind_direction": "--",
                "uv_index": "--",
                "visibility": "--",
                "pressure": "--"
            },
            [],
            []
        )

def clear_screen():
    print("\033c", end="")


# ----------------
# TERMINAL VERSION
# ----------------

if __name__ == "__main__":

    cached_temp_f = "--"
    cached_weather_desc = "Unavailable"
    cached_hourly = []

    last_weather_update = 0
    weather_refresh_seconds = 600

    while True:

        current_time = datetime.now()

        formatted_time = current_time.strftime("%-I:%M %p")
        formatted_date = current_time.strftime("%A, %b %d")

        current_timestamp = time.time()

        if current_timestamp - last_weather_update >= weather_refresh_seconds:

            current_weather, cached_hourly, forecast = get_weather(city)

            cached_temp_f = current_weather["temp_f"]
            cached_weather_desc = current_weather["description"]

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

        seconds_until_next_minute = (
            60 - current_time.second -
            current_time.microsecond / 1_000_000
        )

        time.sleep(seconds_until_next_minute)