from pathlib import Path
from datetime import datetime

import requests
import customtkinter as ctk
from PIL import Image, ImageFilter, ImageDraw

from desk_clock import get_weather, get_weather_icon
from io import BytesIO

BASE_DIR = Path(__file__).parent


# ---------------
# APP Setup
# ---------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()

app.title("Bobcat Smart Display")
app.attributes("-fullscreen", True)


# Colors

BACKGROUND = "#111111"
MAROON = "#501214"
GOLD = "#C8A03A"

app.configure(fg_color=BACKGROUND)


# ----------------
# WEATHER SETTINGS
# ----------------

CITY = "San Marcos"
def get_location_coordinates(city):
    try:
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            "q": city,
            "format": "json",
            "limit": 1
        }

        response = requests.get(
            url,
            params=params,
            headers={"User-Agent": "Bobcat-Smart-Display"},
            timeout=10
        )
        response.raise_for_status()

        results = response.json()

        if results:
            latitude = float(results[0]["lat"])
            longitude = float(results[0]["lon"])
            return latitude, longitude

    except Exception as error:
        print("Location error:", error)

    return None, None

def get_radar_image(city):
    try:
        # Get coordinates for the city
        latitude, longitude = get_location_coordinates(city)

        if latitude is None or longitude is None:
            return None

        # Get the latest RainViewer radar frame
        api_url = "https://api.rainviewer.com/public/weather-maps.json"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()

        latest_frame = data["radar"]["past"][-1]

        host = data["host"]
        path = latest_frame["path"]

        # Build radar image URL centered on the city's coordinates
        radar_url = (
            f"{host}{path}/"
            f"512/6/"
            f"{latitude}/"
            f"{longitude}/"
            f"2/1_1.png" 
        )

        # Download radar image
        radar_response = requests.get(radar_url, timeout=10)
        radar_response.raise_for_status()

        radar_image = Image.open(
            BytesIO(radar_response.content)
        ).convert("RGBA")

        return radar_image

    except Exception as error:
        print("Radar error:", error)
        return None

def load_radar():
    radar_image = get_radar_image(CITY)

    if radar_image is None:
        radar_label.configure(image=None, text="Radar unavailable")
        return
    radar_image = radar_image.resize(
        (900, 500),
        Image.Resampling.LANCZOS
    )

    radar_ctk_image = ctk.CTkImage(
        light_image=radar_image,
        dark_image=radar_image,
        size=(900, 500)
    )

    radar_label.configure(
        image=radar_ctk_image,
        text=""
    )

    # Keep the image in memory
    radar_label.image = radar_ctk_image

WEATHER_REFRESH_SECONDS = 600

cached_temp_f = "--"
cached_weather_desc = "Unavailable"
cached_rain_chance = 0

cached_current_weather = {}
cached_forecast = []
cached_today_hourly = []

# ----------------
# MAIN CONTENT
# ----------------

content_frame = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

content_frame.pack(
    expand=True,
    fill="both"
)


left_frame = ctk.CTkFrame(
    content_frame,
    fg_color="transparent"
)

right_frame = ctk.CTkFrame(
    content_frame,
    fg_color="transparent"
)


left_frame.pack(
    side="left",
    expand=True,
    padx=(120, 40)
)

right_frame.pack(
    side="right",
    expand=True,
    padx=(40, 120)
)


# ----------------
# TIME
# ----------------

time_frame = ctk.CTkFrame(
    left_frame,
    fg_color="transparent"
)

time_frame.pack(
    anchor="w"
)


time_label = ctk.CTkLabel(
    time_frame,
    text="",
    font=("Arial", 90, "bold"),
    text_color="white"
)

time_label.pack(
    side="left"
)


ampm_label = ctk.CTkLabel(
    time_frame,
    text="",
    font=("Arial", 42, "bold"),
    text_color=GOLD
)

ampm_label.pack(
    side="left",
    padx=(10, 0),
    pady=(35, 0)
)


# ----------------
# DATE
# ----------------

date_label = ctk.CTkLabel(
    left_frame,
    text="",
    font=("Arial", 30),
    text_color=GOLD
)

date_label.pack(
    anchor="w",
    pady=(0, 45)
)


# ----------------
# TEMPERATURE
# ----------------

temp_label = ctk.CTkLabel(
    left_frame,
    text="☀ --°F",
    font=("Arial", 50, "bold"),
    text_color="white"
)

temp_label.pack(
    anchor="w"
)


# ----------------
# CONDITIONS
# ----------------

weather_label = ctk.CTkLabel(
    left_frame,
    text="Loading weather...",
    font=("Arial", 30),
    text_color="white"
)

weather_label.pack(
    anchor="w",
    pady=(0, 35)
)


# ----------------
# RAIN CHANCE
# ----------------

rain_label = ctk.CTkLabel(
    left_frame,
    text="🌧 Rain --%",
    font=("Arial", 34),
    text_color="white"
)

rain_label.pack(
    anchor="w"
)


# ----------------
# LOCATION
# ----------------

location_label = ctk.CTkLabel(
    right_frame,
    text="📍 San Marcos, TX",
    text_color=GOLD,
    font=("Arial", 24)
)

location_label.pack(
    anchor="ne",
    padx=20,
    pady=10
)


# ----------------
# BOBCAT + ATMOSPHERIC RED GLOW
# ----------------

logo_path = BASE_DIR / "assets2" / "supercat-logo.png"

logo = Image.open(logo_path).convert("RGBA")

logo_size = (520, 520)

logo = logo.resize(
    logo_size,
    Image.Resampling.LANCZOS
)


def create_bobcat_scene():

    width = 700
    height = 700

    scene = Image.new(
        "RGBA",
        (width, height),
        (17, 17, 17, 255)
    )

    pixels = scene.load()

    center_x = 360
    center_y = 350

    # Large atmospheric red glow

    for y in range(height):

        for x in range(width):

            dx = x - center_x
            dy = y - center_y

            distance = (dx * dx + dy * dy) ** 0.5

            intensity = max(
                0,
                1 - distance / 400
            )

            intensity = intensity ** 2.4

            red = int(95 * intensity)
            green = int(8 * intensity)
            blue = int(18 * intensity)

            base_r = 17
            base_g = 17
            base_b = 17

            pixels[x, y] = (
                min(255, base_r + red),
                min(255, base_g + green),
                min(255, base_b + blue),
                255
            )


    # Smaller brighter center

    center_glow = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0)
    )

    center_pixels = center_glow.load()

    for y in range(height):

        for x in range(width):

            dx = x - center_x
            dy = y - center_y

            distance = (dx * dx + dy * dy) ** 0.5

            intensity = max(
                0,
                1 - distance / 250
            )

            intensity = intensity ** 3

            center_pixels[x, y] = (
                int(120 * intensity),
                int(12 * intensity),
                int(20 * intensity),
                int(80 * intensity)
            )


    scene = Image.alpha_composite(
        scene,
        center_glow
    )


    # ----------------
    # Add Bobcat
    # ----------------

    logo_x = (width - logo.width) // 2
    logo_y = (height - logo.height) // 2

    scene.alpha_composite(
        logo,
        (logo_x, logo_y)
    )

    return scene


bobcat_scene = create_bobcat_scene()


logo_image = ctk.CTkImage(
    light_image=bobcat_scene,
    dark_image=bobcat_scene,
    size=(700, 700)
)


logo_label = ctk.CTkLabel(
    right_frame,
    text="",
    image=logo_image,
    fg_color="transparent"
)

logo_label.pack(
    expand=True
)


# ----------------
# BOTTOM TEXT
# ----------------

tap_label = ctk.CTkLabel(
    app,
    text="—  TAP ANYWHERE TO OPEN HUB  —",
    font=("Arial", 20),
    text_color=GOLD
)

tap_label.pack(
    side="bottom",
    pady=30
)


# ----------------
# LIVE TIME
# ----------------

def update_time():

    now = datetime.now()

    formatted_time = now.strftime("%-I:%M")
    am_pm = now.strftime("%p")
    formatted_date = now.strftime("%A, %B %-d")

    time_label.configure(
        text=formatted_time
    )

    ampm_label.configure(
        text=am_pm
    )

    date_label.configure(
        text=formatted_date
    )

    app.after(
        1000,
        update_time
    )


# ----------------
# LIVE WEATHER
# ----------------

def update_weather():

    global cached_temp_f
    global cached_weather_desc
    global cached_rain_chance
    global cached_current_weather
    global cached_forecast
    global cached_today_hourly

    current_weather, today_hourly, forecast = get_weather(CITY)
    print("CURRENT WEATHER:", current_weather)

    cached_current_weather = current_weather
    cached_today_hourly = today_hourly
    cached_forecast = forecast

    print("HOURLY COUNT:", len(today_hourly))
    print("FORECAST COUNT:", len(forecast))

    cached_temp_f = current_weather["temp_f"]
    cached_weather_desc = current_weather["description"]

    # Find the next applicable rain probability

    current_hour = datetime.now().hour

    rain_chance = 0

    for hour in today_hourly:

        forecast_time = int(hour["time"]) // 100

        if forecast_time >= current_hour:

            rain_chance = int(hour["chanceofrain"])

            break

    cached_rain_chance = rain_chance

    icon = get_weather_icon(cached_weather_desc)


    # Update GUI

    temp_label.configure(
        text=f"{icon} {cached_temp_f}°F"
    )

    weather_label.configure(
        text=cached_weather_desc
    )

    rain_label.configure(
        text=f"🌧 Rain {cached_rain_chance}%"
    )


    # Refresh again in 10 minutes

    app.after(
        WEATHER_REFRESH_SECONDS * 1000,
        update_weather
    )
# ----------------
# SMART HUB
# ----------------

hub_frame = ctk.CTkFrame(app, fg_color=BACKGROUND)

hub_title = ctk.CTkLabel(hub_frame,
    text="SMART HUB",
    font=("Arial", 50, "bold"),
    text_color=GOLD)

hub_title.pack(pady=50)

# ----------------
# WEATHER TILE
# ----------------

weather_tile = ctk. CTkButton( hub_frame,
    text="☀️\nWEATHER",
    font=("Arial", 28, "bold"),
    text_color="white",
    fg_color=MAROON,
    hover_color="#6A181C",
    width=250,
    height=150,
    command=lambda: open_weather())
weather_tile.pack(pady=20)

back_button = ctk.CTkButton(
    hub_frame,
    text="← Back",
    font=("Arial", 24),
    text_color="white",
    fg_color=MAROON,
    hover_color="#6A181C",
    command=lambda: close_hub()
)

back_button.pack(
    anchor="nw",
    padx=40,
    pady=20
)
# ----------------
# OPEN WEATHER
# ----------------

def open_weather():

    # Hide Smart Hub
    hub_frame.pack_forget()

    # Update weather information
    show_weather()

    # Show Weather screen
    weather_frame.pack(
        expand=True,
        fill="both"
    )

    #Load Radar
    load_radar()
# ----------------
# OPEN SMART HUB
# ----------------
def close_hub():

    # Hide Smart Hub
    hub_frame.pack_forget()

    # Show idle screen
    content_frame.pack(
        expand=True,
        fill="both"
    )

    tap_label.pack(
        side="bottom",
        pady=30
    )

def open_hub(event):

    # Hide the idle screen
    content_frame.pack_forget()
    tap_label.pack_forget()

    # Show Smart Hub
    hub_frame.pack(
        expand=True,
        fill="both"
    )

# Make the idle screen clickable
content_frame.bind("<Button-1>", open_hub)
left_frame.bind("<Button-1>", open_hub)
right_frame.bind("<Button-1>", open_hub)
time_frame.bind("<Button-1>", open_hub)

time_label.bind("<Button-1>", open_hub)
ampm_label.bind("<Button-1>", open_hub)
date_label.bind("<Button-1>", open_hub)
temp_label.bind("<Button-1>", open_hub)
weather_label.bind("<Button-1>", open_hub)
rain_label.bind("<Button-1>", open_hub)
location_label.bind("<Button-1>", open_hub)
logo_label.bind("<Button-1>", open_hub)
tap_label.bind("<Button-1>", open_hub)

# ----------------
# WEATHER SCREEN
# ----------------

weather_frame = ctk.CTkFrame(
    app,
    fg_color=BACKGROUND
)


# ----------------
# WEATHER HEADER
# ----------------

weather_header = ctk.CTkFrame(
    weather_frame,
    fg_color="transparent"
)

weather_header.pack(
    fill="x",
    padx=40,
    pady=(20, 10)
)


weather_back_button = ctk.CTkButton(
    weather_header,
    text="← Back",
    font=("Arial", 24),
    text_color="white",
    fg_color=MAROON,
    hover_color="#6A181C",
    width=140,
    command=lambda: close_weather()
)

weather_back_button.pack(
    side="left"
)


weather_title = ctk.CTkLabel(
    weather_header,
    text="WEATHER",
    font=("Arial", 50, "bold"),
    text_color=GOLD
)

weather_title.place(
    relx=0.5,
    rely=0.5,
    anchor="center"
)


# ----------------
# SCROLLABLE WEATHER CONTENT
# ----------------

weather_scroll = ctk.CTkScrollableFrame(
    weather_frame,
    fg_color="transparent"
)

weather_scroll.pack(
    expand=True,
    fill="both",
    padx=60,
    pady=(0, 30)
)

# ----------------
# TOUCH / DRAG SCROLLING
# ----------------

scroll_start_y = 0


def start_scroll(event):

    global scroll_start_y

    scroll_start_y = event.y_root


def drag_scroll(event):

    global scroll_start_y

    difference = scroll_start_y - event.y_root

    if abs(difference) > 1:

        weather_scroll._parent_canvas.yview_scroll(
            int(difference / 2),
            "units"
        )

        scroll_start_y = event.y_root


def bind_scroll(widget):

    widget.bind(
        "<Button-1>",
        start_scroll,
        add="+"
    )

    widget.bind(
        "<B1-Motion>",
        drag_scroll,
        add="+"
    )

    for child in widget.winfo_children():

        bind_scroll(child)


bind_scroll(weather_scroll)
# ----------------
# LOCATION
# ----------------

weather_location = ctk.CTkLabel(
    weather_scroll,
    text="📍 San Marcos, TX",
    font=("Arial", 28),
    text_color=GOLD
)

weather_location.pack(
    pady=(10, 20)
)


# ----------------
# CURRENT CONDITIONS
# ----------------

current_section = ctk.CTkFrame(
    weather_scroll,
    fg_color=MAROON,
    corner_radius=20
)

current_section.pack(
    fill="x",
    pady=10
)


weather_temp = ctk.CTkLabel(
    current_section,
    text="--°F",
    font=("Arial", 80, "bold"),
    text_color="white"
)

weather_temp.pack(
    pady=(25, 0)
)


weather_conditions = ctk.CTkLabel(
    current_section,
    text="Loading weather...",
    font=("Arial", 35),
    text_color="white"
)

weather_conditions.pack(
    pady=(5, 20)
)


# ----------------
# WEATHER DETAILS
# ----------------

details_frame = ctk.CTkFrame(
    current_section,
    fg_color="transparent"
)

details_frame.pack(
    pady=(0, 30)
)


feels_like_label = ctk.CTkLabel(
    details_frame,
    text="Feels like: --°F",
    font=("Arial", 24),
    text_color="white"
)

feels_like_label.grid(
    row=0,
    column=0,
    padx=30,
    pady=10
)


humidity_label = ctk.CTkLabel(
    details_frame,
    text="💧 Humidity: --%",
    font=("Arial", 24),
    text_color="white"
)

humidity_label.grid(
    row=0,
    column=1,
    padx=30,
    pady=10
)


wind_label = ctk.CTkLabel(
    details_frame,
    text="💨 Wind: --",
    font=("Arial", 24),
    text_color="white"
)

wind_label.grid(
    row=1,
    column=0,
    padx=30,
    pady=10
)


uv_label = ctk.CTkLabel(
    details_frame,
    text="☀️ UV Index: --",
    font=("Arial", 24),
    text_color="white"
)

uv_label.grid(
    row=1,
    column=1,
    padx=30,
    pady=10
)


visibility_label = ctk.CTkLabel(
    details_frame,
    text="👁 Visibility: -- mi",
    font=("Arial", 24),
    text_color="white"
)

visibility_label.grid(
    row=2,
    column=0,
    padx=30,
    pady=10
)


pressure_label = ctk.CTkLabel(
    details_frame,
    text="Pressure: -- in",
    font=("Arial", 24),
    text_color="white"
)

pressure_label.grid(
    row=2,
    column=1,
    padx=30,
    pady=10
)


weather_rain = ctk.CTkLabel(
    current_section,
    text="🌧 Rain Chance: --%",
    font=("Arial", 28),
    text_color="white"
)

weather_rain.pack(
    pady=(0, 25)
)


# ----------------
# HOURLY FORECAST
# ----------------

hourly_title = ctk.CTkLabel(
    weather_scroll,
    text="HOURLY FORECAST",
    font=("Arial", 32, "bold"),
    text_color=GOLD
)

hourly_title.pack(
    anchor="w",
    pady=(30, 15)
)


hourly_container = ctk.CTkFrame(
    weather_scroll,
    fg_color="transparent"
)

hourly_container.pack(
    fill="x"
)


# ----------------
# 7-DAY FORECAST
# ----------------

forecast_title = ctk.CTkLabel(
    weather_scroll,
    text="7-DAY FORECAST",
    font=("Arial", 32, "bold"),
    text_color=GOLD
)

forecast_title.pack(
    anchor="w",
    pady=(40, 15)
)


forecast_container = ctk.CTkFrame(
    weather_scroll,
    fg_color="transparent"
)

forecast_container.pack(
    fill="x"
)

# ----------------
# RADAR
# ----------------

radar_title = ctk.CTkLabel(
    weather_scroll,
    text="RADAR",
    font=("Arial", 32, "bold"),
    text_color=GOLD
)

radar_title.pack(
    anchor="w",
    pady=(40, 15)
)


radar_frame = ctk.CTkFrame(
    weather_scroll,
    fg_color="#1A1A1A",
    corner_radius=20
)

radar_frame.pack(
    fill="x",
    pady=(0, 20)
)


radar_label = ctk.CTkLabel(
    radar_frame,
    text="Radar loading...",
    font=("Arial", 24),
    text_color="white"
)

radar_label.pack(
    padx=20,
    pady=20
)


radar_credit = ctk.CTkLabel(
    radar_frame,
    text="Weather data by RainViewer",
    font=("Arial", 14),
    text_color="#AAAAAA"
)

radar_credit.pack(
    pady=(0, 15)
)

# ----------------
# SHOW WEATHER DATA
# ----------------

def show_weather():

    current = cached_current_weather

    if not current:
        return

    icon = get_weather_icon(
        current["description"]
    )

    weather_temp.configure(
        text=f"{icon} {current['temp_f']}°F"
    )

    weather_conditions.configure(
        text=current["description"]
    )

    feels_like_label.configure(
        text=f"Feels like: {current['feels_like_f']}°F"
    )

    humidity_label.configure(
        text=f"💧 Humidity: {current['humidity']}%"
    )

    wind_label.configure(
        text=f"💨 Wind: {current['wind_speed']} mph {current['wind_direction']}"
    )

    uv_label.configure(
        text=f"☀️ UV Index: {current['uv_index']}"
    )

    visibility_label.configure(
        text=f"👁 Visibility: {current['visibility']} mi"
    )

    pressure_label.configure(
        text=f"Pressure: {current['pressure']} in"
    )

    weather_rain.configure(
        text=f"🌧 Rain Chance: {cached_rain_chance}%"
    )


    # ----------------
    # HOURLY FORECAST
    # ----------------

    for widget in hourly_container.winfo_children():
        widget.destroy()

    # Show the next 8 hours
    for index, hour in enumerate(cached_today_hourly[:8]):

        hour_frame = ctk.CTkFrame(
            hourly_container,
            fg_color="#1A1A1A",
            corner_radius=20,
            width=150,
            height=190
        )

        hour_frame.grid(
            row=0,
            column=index,
            padx=8,
            sticky="nsew"
        )

        hourly_container.grid_columnconfigure(
            index,
            weight=1
        )

        forecast_hour = int(hour["time"]) // 100

        if forecast_hour == 0:
            display_time = "12 AM"
        elif forecast_hour < 12:
            display_time = f"{forecast_hour} AM"
        elif forecast_hour == 12:
            display_time = "12 PM"
        else:
            display_time = f"{forecast_hour - 12} PM"

        hour_icon = get_weather_icon(
            hour["weatherDesc"][0]["value"]
        )

        ctk.CTkLabel(
            hour_frame,
            text=display_time,
            font=("Arial", 22, "bold"),
            text_color=GOLD
        ).pack(
            pady=(18, 8)
        )

        ctk.CTkLabel(
            hour_frame,
            text=hour_icon,
            font=("Arial", 42)
        ).pack()

        ctk.CTkLabel(
            hour_frame,
            text=f"{hour['tempF']}°F",
            font=("Arial", 26, "bold"),
            text_color="white"
        ).pack(
            pady=8
        )

        ctk.CTkLabel(
            hour_frame,
            text=f"🌧 {hour['chanceofrain']}%",
            font=("Arial", 19),
            text_color="white"
        ).pack(
            pady=(0, 18)
        )

    # ----------------
    # 7-DAY FORECAST
    # ----------------

    for widget in forecast_container.winfo_children():
        widget.destroy()

    forecast_container.grid_columnconfigure(
            0,
            weight=1
        )


    for index, day in enumerate(cached_forecast):

        day_frame = ctk.CTkFrame(
        forecast_container,
        fg_color="#1A1A1A",
        corner_radius=20
    )

        day_frame.grid(
        row=index,
        column=0,
        padx=5,
        pady=8,
        sticky="ew"
    )

    

        date = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        )

        day_name = date.strftime("%A")

        ctk.CTkLabel(
            day_frame,
            text=day_name,
            font=("Arial", 28, "bold"),
            text_color=GOLD
        ).pack(
            anchor="w",
            padx=25,
            pady=(18, 5)
        )

        ctk.CTkLabel(
            day_frame,
            text=day["description"],
            font=("Arial", 22),
            text_color="white"
        ).pack(
            anchor="w",
            padx=25
        )

        ctk.CTkLabel(
            day_frame,
            text=f"{day['max_temp_f']}°F  /  {day['min_temp_f']}°F",
            font=("Arial", 30, "bold"),
            text_color="white"
        ).pack(
            anchor="w",
            padx=25,
            pady=8
        )

        ctk.CTkLabel(
            day_frame,
            text=f"🌧 {day['rain_chance']}% rain",
            font=("Arial", 21),
            text_color="white"
        ).pack(
            anchor="w",
            padx=25,
            pady=3
        )

        ctk.CTkLabel(
            day_frame,
            text=f"🌅 {day['sunrise']}    🌇 {day['sunset']}",
            font=("Arial", 19),
            text_color="white"
        ).pack(
            anchor="w",
            padx=25,
            pady=(3, 20)
        )
# Enable drag scrolling on all weather content
    bind_scroll(weather_scroll)

# ----------------
# CLOSE WEATHER
# ----------------

def close_weather():

    weather_frame.pack_forget()

    hub_frame.pack(
        expand=True,
        fill="both"
    )
# ----------------
# ESC TO EXIT
# ----------------

def exit_fullscreen(event):

    app.attributes(
        "-fullscreen",
        False
    )


app.bind(
    "<Escape>",
    exit_fullscreen
)


# ----------------
# START APP
# ----------------

update_time()
update_weather()

app.mainloop()