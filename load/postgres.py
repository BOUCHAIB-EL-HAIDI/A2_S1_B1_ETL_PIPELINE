import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql+psycopg://"
    "weather_user:weather_password@postgres:5432/weather_db"
)

engine = create_engine(DATABASE_URL)


def load_cities():
    try:
        cities_df = pd.read_csv("data/silver/cities_clean.csv")

        cities_df.to_sql(
            "cities",
            engine,
            if_exists="append",
            index=False
        )

        print(f"{len(cities_df)} cities loaded successfully.")

    except FileNotFoundError:
        print("Cities file not found.")

    except pd.errors.EmptyDataError:
        print("Cities file is empty.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def load_weather():
    try:
        weather_df = pd.read_csv("data/silver/weather_clean.csv")

        weather_df["date"] = pd.to_datetime(weather_df["date"]).dt.date

        weather_df.to_sql(
            "weather_forecasts",
            engine,
            if_exists="append",
            index=False
        )

        print(f"{len(weather_df)} weather forecasts loaded successfully.")

    except FileNotFoundError:
        print("Weather file not found.")

    except pd.errors.EmptyDataError:
        print("Weather file is empty.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    load_weather()