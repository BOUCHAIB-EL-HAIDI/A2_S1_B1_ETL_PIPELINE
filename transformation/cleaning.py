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


# =========================
# Validate sources
# =========================

def validate_sources(cities, weather_data):

    if len(cities) != len(weather_data):
        raise ValueError(
            f"Source mismatch: "
            f"{len(cities)} cities but "
            f"{len(weather_data)} weather locations."
        )

    print(
        f"Source validation successful: "
        f"{len(cities)} cities / "
        f"{len(weather_data)} weather locations"
    )


# =========================
# Clean cities
# =========================

def clean_cities(cities):

    df = pd.DataFrame(cities)

    # Keep only the columns we need
    df = df[["city", "lat", "lng"]].copy()

    # Convert coordinates to numeric
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

    # Check for invalid coordinates
    invalid_coordinates = (
        df["lat"].isna()
        | df["lng"].isna()
        | ~df["lat"].between(-90, 90)
        | ~df["lng"].between(-180, 180)
    )

    if invalid_coordinates.any():
        raise ValueError(
            f"Found {invalid_coordinates.sum()} cities "
            f"with invalid coordinates."
        )

    # Check duplicate city names
    if df["city"].duplicated().any():
        raise ValueError("Duplicate city names detected.")

    # Create a stable ID AFTER validation
    df = df.reset_index(drop=True)
    df["city_id"] = df.index + 1

    # Rename columns
    df = df.rename(
        columns={
            "lat": "latitude",
            "lng": "longitude"
        }
    )

    # Put city_id first
    df = df[
        [
            "city_id",
            "city",
            "latitude",
            "longitude"
        ]
    ]

    return df


