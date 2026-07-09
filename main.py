from pathlib import Path
import customtkinter as ctk
from PIL import Image
BASE_DIR = Path(__file__).parent
#---------------
#APP Setup
#---------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


app = ctk.CTk()

#Fullscreen window
app.title("Bobcat Smart Display")
app.attributes("-fullscreen",True)

#Colors
BACKGROUND = "#111111" #dark background
MAROON = "#501214" #Maroon
GOLD = "#C8A03A" #muted gold

app.configure(fg_color=BACKGROUND)

# ----------------
# MAIN CONTENT
# ----------------

content_frame = ctk.CTkFrame(
    app,
    fg_color="transparent"
)
content_frame.pack(expand=True, fill="both")

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

# Time
time_label = ctk.CTkLabel(
    left_frame,
    text="4:25 PM",
    font=("Arial", 90, "bold"),
    text_color="white"
)
time_label.pack(anchor="w")

# Date
date_label = ctk.CTkLabel(
    left_frame,
    text="Wednesday, June 3",
    font=("Arial", 28),
    text_color=GOLD
)
date_label.pack(anchor="w", pady=(0, 40))

# Temperature
temp_label = ctk.CTkLabel(
    left_frame,
    text="☀ 83°F",
    font=("Arial", 42),
    text_color="white"
)
temp_label.pack(anchor="w")

# Conditions
weather_label = ctk.CTkLabel(
    left_frame,
    text="Partly Cloudy",
    font=("Arial", 24),
    text_color="white"
)
weather_label.pack(anchor="w", pady=(0, 30))

# Rain Chance
rain_label = ctk.CTkLabel(
    left_frame,
    text="🌧 Rain 35%",
    font=("Arial", 28),
    text_color="white"
)
rain_label.pack(anchor="w")

#Location
location_label = ctk.CTkLabel(right_frame, text = "📍 San Marcos, TX",text_color = GOLD,
                               font = ("Arial", 24))
location_label.pack(anchor = "ne", padx = 20, pady = 10)

#Bobcat 
logo_image = ctk.CTkImage(
    light_image=Image.open("assets2/supercat-logo.png"),
    dark_image=Image.open("assets2/supercat-logo.png"),
    size=(450, 450)
)

logo_label = ctk.CTkLabel(
    right_frame,
    text="",
    image=logo_image
)

logo_label.pack(expand=True)
#Bottom Text

tap_label = ctk.CTkLabel(
    app,
    text="Tap Anywhere to Open Hub",
    font=("Arial", 20),
    text_color="gray"
)

tap_label.pack(
    side="bottom",
    pady=30
)

#-----------------
#ESC to EXit fullscreen
#------------------

def exit_fullscreen(event):
    app.attributes("-fullscreen",False)


app.bind("<Escape>", exit_fullscreen)

#------------
#Run App
#------------
app.mainloop()