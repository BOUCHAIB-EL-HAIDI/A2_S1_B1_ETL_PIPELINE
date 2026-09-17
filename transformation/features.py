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


# Calculate the risk caused by wind speed and wind gusts.
def calculate_wind_risk(row):

    wind_speed = row["wind_speed"]
    wind_gusts = row["wind_gusts"]

    if wind_speed < 40:
        speed_risk = 0
    elif wind_speed < 55:
        speed_risk = 30
    elif wind_speed < 70:
        speed_risk = 60
    else:
        speed_risk = 100

    if wind_gusts < 60:
        gust_risk = 0
    elif wind_gusts < 75:
        gust_risk = 30
    elif wind_gusts < 100:
        gust_risk = 60
    else:
        gust_risk = 100

    return max(speed_risk, gust_risk)


# Convert the wind risk score into a category.
def classify_wind_risk(risk):

    if risk < 25:
        return "Low"
    elif risk < 50:
        return "Moderate"
    elif risk < 75:
        return "High"
    else:
        return "Very High"


# Create all wind-related features.
def calculate_wind_features(df):

    df["wind_risk"] = df.apply(
        calculate_wind_risk,
        axis=1
    )

    df["wind_category"] = df["wind_risk"].apply(
        classify_wind_risk
    )

    return df


# Calculate the global weather risk score.
def calculate_risk_score(df):

    df["risk_score"] = (
        df["temperature_risk"] * 0.30
        + df["rain_risk"] * 0.40
        + df["wind_risk"] * 0.30
    )

    return df


# Convert the global risk score into a risk level.
def classify_risk_level(score):

    if score < 25:
        return "Low"
    elif score < 50:
        return "Moderate"
    elif score < 75:
        return "High"
    else:
        return "Very High"


# Create the final risk level.
def calculate_risk_level(df):

    df["risk_level"] = df["risk_score"].apply(
        classify_risk_level
    )

    return df


# Select only the columns needed for the Gold table.
def prepare_gold_data(df):

    return df[
        [
            "city_id",
            "date",
            "temperature_category",
            "rain_category",
            "wind_category",
            "temperature_risk",
            "rain_risk",
            "wind_risk",
            "risk_score",
            "risk_level"
        ]
    ]


# Load Gold data into PostgreSQL.
# A staging table is used before performing the final UPSERT.
def load_gold_data(df):

    try:

        # Load the DataFrame into a temporary staging table.
        df.to_sql(
            "weather_risks_staging",
            engine,
            if_exists="replace",
            index=False
        )

        # Insert new records and update existing records.
        upsert_query = text("""
            INSERT INTO weather_risks (
                city_id,
                date,
                temperature_category,
                rain_category,
                wind_category,
                temperature_risk,
                rain_risk,
                wind_risk,
                risk_score,
                risk_level
            )
            SELECT
                city_id,
                date,
                temperature_category,
                rain_category,
                wind_category,
                temperature_risk,
                rain_risk,
                wind_risk,
                risk_score,
                risk_level
            FROM weather_risks_staging

            ON CONFLICT (city_id, date)
            DO UPDATE SET
                temperature_category = EXCLUDED.temperature_category,
                rain_category = EXCLUDED.rain_category,
                wind_category = EXCLUDED.wind_category,
                temperature_risk = EXCLUDED.temperature_risk,
                rain_risk = EXCLUDED.rain_risk,
                wind_risk = EXCLUDED.wind_risk,
                risk_score = EXCLUDED.risk_score,
                risk_level = EXCLUDED.risk_level;
        """)

        with engine.begin() as connection:
            connection.execute(upsert_query)

        print(f"{len(df)} Gold records loaded successfully.")

    except Exception as e:
        print(f"Could not load Gold data: {e}")


# Run the complete Gold transformation pipeline.
def main():

    df = load_weather()

    if df.empty:
        return

    df = calculate_temperature_features(df)

    df = calculate_rain_features(df)

    df = calculate_wind_features(df)

    df = calculate_risk_score(df)

    df = calculate_risk_level(df)

    gold_df = prepare_gold_data(df)

    gold_df.to_csv(
        "data/gold/weather_ready.csv",
        index=False
    )

    load_gold_data(gold_df)


if __name__ == "__main__":
    main()