import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = (
    "postgresql+psycopg2://"
    "weather_user:weather_password@postgres:5432/weather_db"
)

engine = create_engine(DATABASE_URL)


def load_weather():
    try:
        weather_df = pd.read_csv("data/silver/weather_clean.csv")
        weather_df["date"] = pd.to_datetime(weather_df["date"]).dt.date

        records = weather_df.to_dict(orient="records")

        upsert_query = text("""
            INSERT INTO weather_forecasts (
                city_id,
                date,
                temperature_max,
                temperature_min,
                precipitation,
                precipitation_probability,
                wind_speed,
                wind_gusts,
                weather_code
            )
            VALUES (
                :city_id,
                :date,
                :temperature_max,
                :temperature_min,
                :precipitation,
                :precipitation_probability,
                :wind_speed,
                :wind_gusts,
                :weather_code
            )
            ON CONFLICT (city_id, date)
            DO UPDATE SET
                temperature_max = EXCLUDED.temperature_max,
                temperature_min = EXCLUDED.temperature_min,
                precipitation = EXCLUDED.precipitation,
                precipitation_probability = EXCLUDED.precipitation_probability,
                wind_speed = EXCLUDED.wind_speed,
                wind_gusts = EXCLUDED.wind_gusts,
                weather_code = EXCLUDED.weather_code;
        """)

        with engine.begin() as connection:
            connection.execute(upsert_query, records)

        print(f"{len(weather_df)} weather forecasts upserted successfully.")

    except FileNotFoundError:
        print("Weather file not found.")

    except pd.errors.EmptyDataError:
        print("Weather file is empty.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
def load_data():
    load_weather()