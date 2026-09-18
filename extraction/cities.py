import requests

URL = "https://simplemaps.com/static/data/country-cities/ma/ma.csv"
OUTPUT_FILE = "data/bronze/cities/ma_cities.csv"


def extract_cities():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"

        print("Request successful")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            file.write(response.text)

        print("Cities data extracted successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    except OSError as e:
        print(f"Could not save cities data: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")