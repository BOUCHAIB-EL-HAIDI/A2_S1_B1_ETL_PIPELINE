# Quelles villes auront les températures les plus élevées ?
SELECT
    c.city,
    MAX(wf.temperature_max) AS max_temperature
FROM weather_forecasts wf
JOIN cities c
    ON wf.city_id = c.city_id
GROUP BY c.city
ORDER BY max_temperature DESC;

# Which cities will have the highest precipitation?

SELECT
    c.city,
    MAX(wf.precipitation) AS max_precipitation
FROM weather_forecasts wf
JOIN cities c
    ON wf.city_id = c.city_id
GROUP BY c.city
ORDER BY max_precipitation DESC;

# Which cities have the highest average risk?

SELECT
    c.city,
    ROUND(AVG(wr.risk_score), 2) AS average_risk
FROM weather_risks wr
JOIN cities c
    ON wr.city_id = c.city_id
GROUP BY c.city
ORDER BY average_risk DESC;
# Which periods have the highest risk?

SELECT
    date,
    MAX(risk_score) AS max_risk
FROM weather_risks
GROUP BY date
ORDER BY max_risk DESC;

# For each city, which period has the highest risk?


SELECT
    c.city,
    wr.date,
    wr.risk_score,
    wr.risk_level
FROM weather_risks wr
JOIN cities c
    ON wr.city_id = c.city_id
ORDER BY c.city, wr.risk_score DESC;



