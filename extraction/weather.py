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


def main():

    # Read all Moroccan cities
    with open(CITIES_FILE, "r", encoding="utf-8") as file:
        cities = list(csv.DictReader(file))

    # Get all coordinates
    latitudes = ",".join(city["lat"] for city in cities)
    longitudes = ",".join(city["lng"] for city in cities)

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "daily": DAILY_VARIABLES,
        "timezone": "Africa/Casablanca"
    }

    try:
        # ONE request for all cities
        response = requests.get(
            URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        # Convert JSON response to Python object
        data = response.json()

        # Save raw response
        with open(WEATHER_FILE, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

        print("Weather data extracted successfully.")
        print(f"Cities requested: {len(cities)}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    except ValueError as e:
        print(f"Invalid JSON response: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()