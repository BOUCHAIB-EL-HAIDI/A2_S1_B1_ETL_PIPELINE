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
