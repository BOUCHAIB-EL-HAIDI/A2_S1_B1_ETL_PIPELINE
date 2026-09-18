import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from datetime import timedelta
import pydeck as pdk

DATABASE_URL = (
    "postgresql+psycopg://"
    "weather_user:weather_password@postgres:5432/weather_db"
)

engine = create_engine(DATABASE_URL)


query = """
    SELECT
        wr.city_id,
        c.city,
        c.latitude,
        c.longitude,
        wr.date,
        wf.temperature_max,
        wf.temperature_min,
        wf.precipitation,
        wf.precipitation_probability,
        wf.wind_speed,
        wf.wind_gusts,
        wf.weather_code,
        wr.temperature_category,
        wr.rain_category,
        wr.wind_category,
        wr.temperature_risk,
        wr.rain_risk,
        wr.wind_risk,
        wr.risk_score,
        wr.risk_level
    FROM weather_risks wr
    JOIN cities c
        ON wr.city_id = c.city_id
    JOIN weather_forecasts wf
        ON wr.city_id = wf.city_id
        AND wr.date = wf.date
"""

df = pd.read_sql(query, engine)

st.title("Weather Risk Dashboard")

st.header("Weather Risk Analysis")

st.write("Weather analysis for delivery operations.")

st.header("Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Cities",
    df["city"].nunique()
)

col2.metric(
    "Max Temperature",
    f"{df['temperature_max'].max():.1f} °C"
)

col3.metric(
    "Max Precipitation",
    f"{df['precipitation'].max():.1f} mm"
)

col4.metric(
    "Risk Periods",
    (df["risk_level"] != "Low").sum()
)

highest_risk_city = df.loc[
    df["risk_score"].idxmax(),
    "city"
]

col5.metric(
    "Highest Risk City",
    highest_risk_city
)


df["date"] = pd.to_datetime(df["date"]).dt.date



st.dataframe(df)
