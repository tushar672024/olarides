import streamlit as st
import pandas as pd
import datetime
import joblib
import holidays
import pytz
import requests

# Load the model
model = joblib.load("model/final_model.pkl")

# Define function to get real-time weather data using OpenWeatherMap API
def get_weather(api_key, city="Delhi"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        windspeed = data["wind"]["speed"]
        weather_main = data["weather"][0]["main"]
        return weather_main, temp, humidity, windspeed
    except:
        return "Clear", 25, 60, 3

# Map weather to int if needed (match your model's encoding)
weather_map = {
    "Clear": 0,
    "Clouds": 1,
    "Rain": 2,
    "Snow": 3,
    "Drizzle": 4,
    "Thunderstorm": 5,
    "Mist": 6,
    "Haze": 7,
    "Fog": 8
}

# Main app
st.title("🚲 Ola Ride Demand Forecasting")

api_key = st.text_input("Enter your OpenWeatherMap API key", type="password")
if not api_key:
    st.warning("Please enter your API key to continue.")
    st.stop()

# Get real-time info
now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
day = now.day
month = now.month
year = now.year
weekday = now.weekday()
am_pm = 0 if now.hour < 12 else 1
season = (month % 12 + 3) // 3  # Spring:1, Summer:2, Fall:3, Winter:4
is_holiday = 1 if now.date() in holidays.India() else 0

# Get weather
weather_main, temp, humidity, windspeed = get_weather(api_key)
weather = weather_map.get(weather_main, 0)

# Casual users (for now, random placeholder or slider)
casual = st.slider("Estimate of casual riders (optional)", 0, 1000, 100)

# Display values
st.write("### Auto-filled features")
st.write(f"**Date/Time:** {now}")
st.write(f"**Season:** {season}, **Weather:** {weather_main}, **Temp:** {temp}°C, **Humidity:** {humidity}%, **WindSpeed:** {windspeed} m/s")
st.write(f"**Casual Users:** {casual}, **AM/PM:** {'AM' if am_pm == 0 else 'PM'}, **Holiday:** {is_holiday}")

# Prediction
if st.button("Predict Demand"):
    features = [[
        season, weather, temp, humidity, windspeed, casual,
        day, month, year, weekday, am_pm, is_holiday
    ]]

    prediction = model.predict(features)[0]
    st.success(f"🔮 Predicted Bike Demand: **{int(prediction)} rides**")
