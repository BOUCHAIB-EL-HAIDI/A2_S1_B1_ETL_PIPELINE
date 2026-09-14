import csv
import json
import requests

CITIES_FILE = "data/bronze/cities/ma_cities.csv"
WEATHER_FILE = "data/bronze/weather/weather.json"

URL = "https://api.open-meteo.com/v1/forecast"

DAILY_VARIABLES = ",".join([
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "weather_code"
])
