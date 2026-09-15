import csv
import json
import pandas as pd


# =========================
# File paths
# =========================

CITIES_FILE = "data/bronze/cities/ma_cities.csv"
WEATHER_FILE = "data/bronze/weather/weather.json"

CITIES_SILVER = "data/silver/cities_clean.csv"
WEATHER_SILVER = "data/silver/weather_clean.csv"
JOINED_SILVER = "data/silver/weather_joined.csv"


# =========================
# Load Bronze data
# =========================

def load_cities(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    except FileNotFoundError:
        raise FileNotFoundError(f"Cities file not found: {filename}")

    except UnicodeDecodeError:
        raise ValueError(f"Could not decode cities file: {filename}")

    except csv.Error as e:
        raise ValueError(f"Invalid CSV file: {e}")


def load_weather(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        raise FileNotFoundError(f"Weather file not found: {filename}")

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")


