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
