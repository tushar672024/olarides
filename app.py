import streamlit as st
import pandas as pd
import joblib
import datetime
import requests

# Optional: OpenWeather API Key (Leave empty if not using)
API_KEY = ""  # ← Add your key here if using OpenWeather API

# Load trained model
model = joblib.load("final_model.pkl")

# Get current datetime
now = datetime.datetime.now()

# Functions
def get_season(month):
    if month in [12, 1, 2]:
        return 1  # Winter
    elif month in [3, 4, 5]:
        return 2  # Spring
    elif month in [6, 7, 8]:
        return 3  # Summer
    else:
        return 4  # Fall

def get_weather_data():
    if API_KEY:
        try:
            city = "Delhi"  # Change as needed
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()

            temp = data['main']['temp']
            humidity = data['main']['humidity']
            windspeed = data['wind']['speed']
            weather_code = data['weather'][0]['id']

            # Simplified weather mapping
            if weather_code < 700:
                weather = 1  # Rain/Snow/etc.
            elif 700 <= weather_code < 800:
                weather = 2  # Mist/Fog/etc.
            elif weather_code == 800:
                weather = 3  # Clear
            else:
                weather = 4  # Cloudy
            return temp, humidity, windspeed, weather
        except:
            return 25.0, 60, 10.0, 1  # Defaults if API fails
    else:
        # Without API, use manual or mock data
        return 25.0, 60, 10.0, 1  # Replace with any default or calculated values

# UI
st.title("Bike Ride Demand Predictor")

st.write("This app predicts ride demand using current weather and time info.")

# Input Features
temp, humidity, windspeed, weather = get_weather_data()

# Manual override (optional)
st.subheader("Override inputs (Optional):")
temp = st.number_input("Temperature (°C)", value=temp)
humidity = st.number_input("Humidity (%)", value=humidity)
windspeed = st.number_input("Wind Speed (km/h)", value=windspeed)
weather = st.selectbox("Weather", [1, 2, 3, 4], format_func=lambda x: ["Rainy", "Mist", "Clear", "Cloudy"][x-1])

# Auto Inputs
season = get_season(now.month)
casual = 100  # Replace with logic or leave fixed
day = now.day
month = now.month
year = now.year
weekday = now.weekday()  # Monday = 0
am_or_pm = 0 if now.hour < 12 else 1
holidays = 1 if now.weekday() in [6] else 0  # Sunday is holiday

# Show gathered features
if st.checkbox("Show features used for prediction"):
    st.write({
        "season": season,
        "weather": weather,
        "temp": temp,
        "humidity": humidity,
        "windspeed": windspeed,
        "casual": casual,
        "day": day,
        "month": month,
        "year": year,
        "weekday": weekday,
        "am_or_pm": am_or_pm,
        "holidays": holidays,
    })

# Prepare input
input_df = pd.DataFrame([[
    season, weather, temp, humidity, windspeed, casual,
    day, month, year, weekday, am_or_pm, holidays
]], columns=[
    "season", "weather", "temp", "humidity", "windspeed", "casual",
    "day", "month", "year", "weekday", "am_or_pm", "holidays"
])

# Predict
if st.button("Predict Demand"):
    prediction = model.predict(input_df)[0]
    st.success(f"Predicted Ride Demand: {int(prediction)}")
