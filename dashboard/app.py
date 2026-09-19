import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from datetime import timedelta, date
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

with st.sidebar:
    st.header("Filters")

    selected_city = st.selectbox(
        "City",
        ["All"] + sorted(df["city"].unique().tolist())
    )

    min_date = df["date"].min()
    max_date = df["date"].max()

    selected_from = st.date_input(
        "From",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

    selected_to = st.date_input(
        "To",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

    available_dates = sorted(
        df[
            (df["date"] >= selected_from)
            & (df["date"] <= selected_to)
        ]["date"].unique()
    )

    selected_date = st.selectbox(
        "Date",
        ["All"] + available_dates
    )

    selected_risk = st.selectbox(
        "Risk level",
        [
            "All",
            "Low",
            "Moderate",
            "High",
            "Very High"
        ]
    )

filtered_df = df.copy()

filtered_df = filtered_df[
    (filtered_df["date"] >= selected_from)
    & (filtered_df["date"] <= selected_to)
]

if selected_date != "All":
    filtered_df = filtered_df[
        filtered_df["date"] == selected_date
    ]

if selected_city != "All":
    filtered_df = filtered_df[
        filtered_df["city"] == selected_city
    ]

if selected_risk != "All":
    filtered_df = filtered_df[
        filtered_df["risk_level"] == selected_risk
    ]



st.header("Filtered Weather Data")

st.dataframe(filtered_df)

st.header("Weather Risk Map")



map_df = (
    filtered_df
    .sort_values("risk_score", ascending=False)
    .drop_duplicates("city")
    .copy()
)


risk_colors = {
    "Low": [0, 180, 0],
    "Moderate": [255, 200, 0],
    "High": [255, 140, 0],
    "Very High": [220, 0, 0]
}

map_df["color"] = map_df["risk_level"].map(risk_colors)


layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position="[longitude, latitude]",
    get_fill_color="color",
    get_radius=10000,
    pickable=True
)


view_state = pdk.ViewState(
    latitude=31.8,
    longitude=-7.1,
    zoom=5.2
)


deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": """
            <b>{city}</b><br/>
            Risk level: {risk_level}<br/>
            Risk score: {risk_score}<br/>
            Date: {date}
        """
    }
)


st.pydeck_chart(deck)

st.markdown(
    """
    **Risk Level**

    🟢 Low &nbsp;&nbsp;
    🟡 Moderate &nbsp;&nbsp;
    🟠 High &nbsp;&nbsp;
    🔴 Very High
    """
)

st.header("High and Very High Risk Cities")

high_risk_df = filtered_df[
    filtered_df["risk_level"].isin(["High", "Very High"])
]

risk_by_city = (
    high_risk_df
    .groupby(["city", "risk_level"])["risk_score"]
    .max()
    .reset_index()
    .sort_values("risk_score", ascending=False)
)

st.dataframe(risk_by_city)