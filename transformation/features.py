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


# Calculate the risk caused by high temperatures.
def calculate_heat_risk(temperature_max):

    if temperature_max < 34:
        return 0
    elif temperature_max < 38:
        return 25
    elif temperature_max < 40:
        return 60
    else:
        return 100


# Calculate the risk caused by low temperatures.
def calculate_cold_risk(temperature_min):

    if temperature_min > 8:
        return 0
    elif temperature_min > 5:
        return 25
    elif temperature_min > 0:
        return 60
    else:
        return 100


# Calculate the final temperature risk using the strongest risk between heat and cold.
def calculate_temperature_risk(row):

    heat_risk = calculate_heat_risk(row["temperature_max"])
    cold_risk = calculate_cold_risk(row["temperature_min"])

    return max(heat_risk, cold_risk)


# Convert the temperature risk score into a category.
def classify_temperature_risk(risk):

    if risk < 25:
        return "Normal"
    elif risk < 50:
        return "Moderate"
    elif risk < 75:
        return "High"
    else:
        return "Very High"


# Create all temperature-related features.
def calculate_temperature_features(df):

    df["temperature_risk"] = df.apply(
        calculate_temperature_risk,
        axis=1
    )

    df["temperature_category"] = df["temperature_risk"].apply(
        classify_temperature_risk
    )

    return df


# Calculate the risk caused by daily precipitation.
def calculate_rain_risk(precipitation):

    if precipitation <= 5:
        return 0
    elif precipitation <= 20:
        return 30
    elif precipitation <= 40:
        return 60
    else:
        return 100


# Convert the rain risk score into a category.
def classify_rain_risk(risk):

    if risk < 25:
        return "Low"
    elif risk < 50:
        return "Moderate"
    elif risk < 75:
        return "High"
    else:
        return "Very High"


# Create all rain-related features.
def calculate_rain_features(df):

    df["rain_risk"] = df["precipitation"].apply(
        calculate_rain_risk
    )

    df["rain_category"] = df["rain_risk"].apply(
        classify_rain_risk
    )

    return df


