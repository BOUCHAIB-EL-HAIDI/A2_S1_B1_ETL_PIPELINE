import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql+psycopg://"
    "weather_user:weather_password@postgres:5432/weather_db"
)

engine = create_engine(DATABASE_URL)

query = """
    SELECT
        wr.city_id,
        c.city,
        wr.date,
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
"""

df = pd.read_sql(query, engine)

st.title("Weather Risk Dashboard")
st.write("Connected to PostgreSQL.")
st.dataframe(df)
