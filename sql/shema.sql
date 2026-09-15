

-- 1. Cities


CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY,

    city VARCHAR(100) NOT NULL,

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,

    CONSTRAINT chk_city_latitude
        CHECK (latitude BETWEEN -90 AND 90),

    CONSTRAINT chk_city_longitude
        CHECK (longitude BETWEEN -180 AND 180)
);


-- 2. Weather Forecasts


CREATE TABLE IF NOT EXISTS weather_forecasts (
    city_id INTEGER NOT NULL,

    date DATE NOT NULL,

    temperature_max DOUBLE PRECISION,

    temperature_min DOUBLE PRECISION,

    precipitation DOUBLE PRECISION,

    precipitation_probability DOUBLE PRECISION,

    wind_speed DOUBLE PRECISION,

    wind_gusts DOUBLE PRECISION,

    weather_code INTEGER,

    CONSTRAINT pk_weather_forecasts
        PRIMARY KEY (city_id, date),

    CONSTRAINT fk_weather_city
        FOREIGN KEY (city_id)
        REFERENCES cities(city_id),

    CONSTRAINT chk_temperature
        CHECK (temperature_min <= temperature_max),

    CONSTRAINT chk_precipitation
        CHECK (precipitation >= 0),

    CONSTRAINT chk_precipitation_probability
        CHECK (
            precipitation_probability BETWEEN 0 AND 100
        ),

    CONSTRAINT chk_wind_speed
        CHECK (wind_speed >= 0),

    CONSTRAINT chk_wind_gusts
        CHECK (wind_gusts >= 0)
);




GOLD - WEATHER RISK


CREATE TABLE IF NOT EXISTS weather_risks (
    city_id INTEGER NOT NULL,

    date DATE NOT NULL,

    temperature_category VARCHAR(30),

    rain_category VARCHAR(30),

    wind_category VARCHAR(30),

    temperature_risk DOUBLE PRECISION NOT NULL,

    rain_risk DOUBLE PRECISION NOT NULL,

    wind_risk DOUBLE PRECISION NOT NULL,

    risk_score DOUBLE PRECISION NOT NULL,

    risk_level VARCHAR(20) NOT NULL,

    CONSTRAINT pk_weather_risks
        PRIMARY KEY (city_id, date),

    CONSTRAINT fk_risk_city
        FOREIGN KEY (city_id)
        REFERENCES cities(city_id),

    CONSTRAINT chk_temperature_risk
        CHECK (temperature_risk BETWEEN 0 AND 100),

    CONSTRAINT chk_rain_risk
        CHECK (rain_risk BETWEEN 0 AND 100),

    CONSTRAINT chk_wind_risk
        CHECK (wind_risk BETWEEN 0 AND 100),

    CONSTRAINT chk_risk_score
        CHECK (risk_score BETWEEN 0 AND 100),

    CONSTRAINT chk_risk_level
        CHECK (
            risk_level IN (
                'Low',
                'Moderate',
                'High',
                'Very High'
            )
        )
);






