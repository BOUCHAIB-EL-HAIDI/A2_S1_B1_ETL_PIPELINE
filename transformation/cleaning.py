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


# =========================
# Flatten weather JSON
# =========================

def flatten_weather_data(cities, weather_data):

    rows = []

    for city_index, city in enumerate(cities):

        city_id = city_index + 1

        daily = weather_data[city_index]["daily"]

        for i in range(len(daily["time"])):

            row = {
                "city_id": city_id,
                "date": daily["time"][i],

                "temperature_max":
                    daily["temperature_2m_max"][i],

                "temperature_min":
                    daily["temperature_2m_min"][i],

                "precipitation":
                    daily["precipitation_sum"][i],

                "precipitation_probability":
                    daily["precipitation_probability_max"][i],

                "wind_speed":
                    daily["wind_speed_10m_max"][i],

                "wind_gusts":
                    daily["wind_gusts_10m_max"][i],

                "weather_code":
                    daily["weather_code"][i]
            }

            rows.append(row)

    return pd.DataFrame(rows)


# =========================
# Clean weather
# =========================

def clean_weather(df):

    df = df.copy()

    # Convert date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Numeric columns
    numeric_columns = [
        "temperature_max",
        "temperature_min",
        "precipitation",
        "precipitation_probability",
        "wind_speed",
        "wind_gusts",
        "weather_code"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Check missing values created by conversion
    missing_values = df.isna().sum()

    print("\nMissing values after conversion:")
    print(missing_values[missing_values > 0])

    # Remove rows with missing critical values
    df = df.dropna(
        subset=[
            "city_id",
            "date"
        ]
    )

    # Remove exact duplicates
    df = df.drop_duplicates()

    # One forecast per city/day
    df = df.drop_duplicates(
        subset=["city_id", "date"]
    )

    # =========================
    # Data quality rules
    # =========================

    invalid_temperature = (
        df["temperature_min"] >
        df["temperature_max"]
    )

    invalid_precipitation = (
        df["precipitation"] < 0
    )

    invalid_probability = (
        (df["precipitation_probability"] < 0)
        |
        (df["precipitation_probability"] > 100)
    )

    invalid_wind = (
        (df["wind_speed"] < 0)
        |
        (df["wind_gusts"] < 0)
    )

    invalid_rows = (
        invalid_temperature
        |
        invalid_precipitation
        |
        invalid_probability
        |
        invalid_wind
    )

    print(
        f"\nInvalid weather rows: "
        f"{invalid_rows.sum()}"
    )

    # Remove invalid rows
    df = df[~invalid_rows].copy()

    return df


