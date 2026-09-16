import pandas as pd
from sqlalchemy import create_engine, text


# Connect to the PostgreSQL database.
DATABASE_URL = (
    "postgresql+psycopg://"
    "weather_user:weather_password@postgres:5432/weather_db"
)

engine = create_engine(DATABASE_URL)


# Load all weather data from PostgreSQL.
def load_weather():
    query = "SELECT * FROM weather_forecasts"
    try:
        df = pd.read_sql(query, engine)

        print(f"{len(df)} weather records loaded from PostgreSQL.")

        return df

    except Exception as e:
        print(f"Could not load weather data: {e}")
        return pd.DataFrame()


