# 🌤️ Morocco Weather ETL Pipeline & Multi-Hazard Risk Analytics

An automated end-to-end ETL pipeline built with Python, PostgreSQL, Docker, and Streamlit. The pipeline extracts 7-day daily weather forecasts for Moroccan cities via Open-Meteo, transforms and cleans data following the **Medallion Architecture (Bronze ➔ Silver ➔ Gold)**, computes multi-hazard weather risk scores, stores structured data into PostgreSQL, and provides a real-time Streamlit dashboard.

---

## 🏛️ Medallion Architecture

```
[ SimpleMaps API / Open-Meteo API ]
                │
                ▼
        [ Bronze Layer ]  📦 Raw JSON & CSV Data Storage
                │
                ▼
        [ Silver Layer ]  🧹 Cleaning, Normalization & Merging
                │
                ▼
        [ Gold Layer ]    ⚡ Feature Engineering & Multi-Hazard Risk Scoring
                │
                ▼
       [ PostgreSQL DB ]  🗄️ Persistent Relational Storage (Dockerized)
                │
                ▼
      [ Streamlit Board ] 📊 Interactive Web Dashboard & Analytics
```

### 1. Extraction (Bronze Layer)
- `extraction/cities.py`: Extracts Moroccan cities reference data (names, latitudes, longitudes).
- `extraction/weather.py`: Queries the Open-Meteo API for 7-day weather forecasts for all Moroccan cities in a single batch request, saving raw JSON responses.

### 2. Transformation (Silver Layer)
- `transformation/cleaning.py`: Cleans raw city data, standardizes coordinates, normalizes weather JSON into tabular records, casts data types, and produces merged datasets (`cities_clean.csv`, `weather_clean.csv`, `weather_joined.csv`).

### 3. Feature Engineering & Risk Scoring (Gold Layer)
- `transformation/features.py`: Loads weather forecasts directly from PostgreSQL, computes individual hazard risks and a composite risk score (0–100), exports results to `data/gold/weather_ready.csv`, and upserts records back into the `weather_risks` table using a staging table strategy:
  - **Temperature Risk**: Evaluates heatwave and extreme cold thresholds.
  - **Precipitation Risk**: Evaluates rainfall volume and precipitation probabilities.
  - **Wind Risk**: Evaluates wind speed and maximum gusts.
  - **Risk Categorization**: Assigns qualitative levels (`Low`, `Moderate`, `High`, `Very High`).

### 4. Database Loading & Schema
- `load/postgres.py`: Loads validated silver datasets directly into PostgreSQL tables via SQLAlchemy using an UPSERT strategy (`ON CONFLICT DO UPDATE`) on `(city_id, date)`. Exposes a unified `load_data()` entry-point called by the Airflow DAG.
- `sql/shema.sql`: Relational database schema with primary keys, foreign keys, and indexes for `cities`, `weather_forecasts`, and `weather_risks`.
- `sql/analysis.sql`: Analytical SQL queries for aggregating risk metrics.

### 5. Workflow Orchestration (Airflow)
- `dags/weather_pipeline.py`: Apache Airflow DAG orchestrating the end-to-end pipeline. Tasks execute in this order:
  ```
  extract_cities >> extract_weather >> clean_data >> load_data >> calculate_risks
  ```
  Scheduled weekly (`0 0 * * 0`) using the `Africa/Casablanca` timezone.

### 6. Web Dashboard
- `dashboard/app.py`: Interactive Streamlit application connecting directly to PostgreSQL to display city-level forecasts, key performance indicators, risk evaluation, and an interactive geographic map using PyDeck.

### 7. Architecture & UML
- `Uml/class diagrame weather.png`: Class and system architecture diagram modeling the pipeline components.

---

## 🚀 Quick Start with Docker

### Prerequisites
- Docker & Docker Compose

### Run the Stack
```bash
docker-compose up -d --build
```

### Services
| Service | URL / Port | Description |
|---|---|---|
| **Streamlit Dashboard** | `http://localhost:8501` | Interactive analytics dashboard |
| **Apache Airflow** | `http://localhost:8080` | Pipeline orchestration & DAG management (built from `Dockerfile.airflow`) |
| **pgAdmin 4** | `http://localhost:5050` | Database web manager (`admin@example.com` / `admin`) |
| **PostgreSQL** | `localhost:5432` | Relational database (`weather_user` / `weather_password`) |

> **Note**: Airflow runs as a standalone container built from `Dockerfile.airflow`. All pipeline source folders (`dags/`, `extraction/`, `transformation/`, `load/`, `data/`) are mounted directly into the Airflow container via Docker volumes.

---

## 💻 Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run extraction & transformations:
   ```bash
   python extraction/cities.py
   python extraction/weather.py
   python transformation/cleaning.py
   python transformation/features.py
   ```
4. Start dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```
