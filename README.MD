# Morocco Weather ETL Pipeline and Multi-Hazard Risk Analytics

An automated end-to-end ETL pipeline built with Python, PostgreSQL, Docker, and Streamlit. The pipeline extracts 7-day daily weather forecasts for Moroccan cities via Open-Meteo, transforms and cleans data following the Medallion Architecture (Bronze to Silver to Gold), computes multi-hazard weather risk scores, stores structured data into PostgreSQL, and provides a real-time Streamlit dashboard.

---

## Medallion Architecture

```
[ SimpleMaps API / Open-Meteo API ]
                |
                v
        [ Bronze Layer ]  Raw JSON and CSV Data Storage
                |
                v
        [ Silver Layer ]  Cleaning, Normalization and Merging
                |
                v
        [ Gold Layer ]    Feature Engineering and Multi-Hazard Risk Scoring
                |
                v
       [ PostgreSQL DB ]  Persistent Relational Storage (Dockerized)
                |
                v
      [ Streamlit Board ] Interactive Web Dashboard and Analytics
```

### 1. Extraction (Bronze Layer)
- `extraction/cities.py`: Extracts Moroccan cities reference data (names, latitudes, longitudes).
- `extraction/weather.py`: Queries the Open-Meteo API for 7-day weather forecasts for all Moroccan cities in a single batch request, saving raw JSON responses.

### 2. Transformation (Silver Layer)
- `transformation/cleaning.py`: Cleans raw city data, standardizes coordinates, normalizes weather JSON into tabular records, casts data types, and produces merged datasets (`cities_clean.csv`, `weather_clean.csv`, `weather_joined.csv`).

### 3. Feature Engineering and Risk Scoring (Gold Layer)
- `transformation/features.py`: Loads weather forecasts directly from PostgreSQL, computes individual hazard risks and a composite risk score (0-100), exports results to `data/gold/weather_ready.csv`, and upserts records back into the `weather_risks` table using a staging table strategy:
  - **Temperature Risk**: Evaluates heatwave and extreme cold thresholds.
  - **Precipitation Risk**: Evaluates rainfall volume and precipitation probabilities.
  - **Wind Risk**: Evaluates wind speed and maximum gusts.
  - **Risk Categorization**: Assigns qualitative levels (`Low`, `Moderate`, `High`, `Very High`).

### 4. Database Loading and Schema
- `load/postgres.py`: Loads validated silver datasets directly into PostgreSQL tables via SQLAlchemy using an UPSERT strategy (`ON CONFLICT DO UPDATE`) on `(city_id, date)`. Exposes a unified `load_data()` entry-point called by the Airflow DAG.
- `sql/shema.sql`: Relational database schema with primary keys, foreign keys, and indexes for `cities`, `weather_forecasts`, and `weather_risks`.
- `sql/analysis.sql`: Analytical SQL queries for aggregating risk metrics.

### 5. Workflow Orchestration (Airflow)
- `dags/weather_pipeline.py`: Apache Airflow DAG orchestrating the end-to-end pipeline. Tasks execute in this order:

```
extract_cities >> extract_weather >> clean_data >> load_data >> calculate_risks
```

Scheduled weekly every Sunday at midnight using the Africa/Casablanca timezone.

### 6. Web Dashboard
- `dashboard/app.py`: Interactive Streamlit application connecting directly to PostgreSQL to display city-level forecasts, key performance indicators, risk evaluation, and an interactive geographic map using PyDeck.

### 7. Architecture and UML
- `Uml/class diagrame weather.png`: Class and system architecture diagram modeling the pipeline components.

---

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose

### Environment Setup

Before running the stack, create a `.env` file at the project root and set your own credentials:

```env
POSTGRES_DB=weather_db
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password

PGADMIN_DEFAULT_EMAIL=your_email@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
```

> **Security**: Never commit your `.env` file. It is already listed in `.gitignore`.
> The default credentials shown in `docker-compose.yml` are for local development only.
> Always use strong, unique credentials for any shared or production environment.

### Run the Stack

```bash
docker-compose up -d --build
```

### Services

| Service | URL / Port | Description |
|---|---|---|
| **Streamlit Dashboard** | `http://localhost:8501` | Interactive analytics dashboard |
| **Apache Airflow** | `http://localhost:8080` | Pipeline orchestration and DAG management (built from `Dockerfile.airflow`) |
| **pgAdmin 4** | `http://localhost:5050` | Database web manager (credentials set in `.env`) |
| **PostgreSQL** | `localhost:5432` | Relational database (credentials set in `.env`) |

> **Note**: Airflow runs as a standalone container built from `Dockerfile.airflow`. All pipeline source folders (`dags/`, `extraction/`, `transformation/`, `load/`, `data/`) are mounted directly into the Airflow container via Docker volumes.

---

## Local Development

The entire pipeline is **Dockerized and orchestrated by Apache Airflow** - there is no need to run scripts manually. Simply bring up the stack and let Airflow handle execution automatically.

### 1. Configure credentials
Create a `.env` file at the project root (see Environment Setup above).

### 2. Start all services
```bash
docker-compose up -d --build
```

### 3. Open the Airflow UI
Navigate to [http://localhost:8080](http://localhost:8080) and log in.

### 4. Trigger the pipeline
Find the `weather_pipeline` DAG and click **Trigger DAG**. Airflow will automatically run all pipeline tasks in the following order:

```
extract_cities >> extract_weather >> clean_data >> load_data >> calculate_risks
```

The pipeline is also scheduled to run **automatically every Sunday at midnight** (Africa/Casablanca timezone).

### 5. View the dashboard
Once the pipeline has completed, open [http://localhost:8501](http://localhost:8501) to explore the Streamlit analytics dashboard.

### 6. Inspect the database
Use **pgAdmin 4** at [http://localhost:5050](http://localhost:5050) and log in with the credentials you defined in your `.env` file to browse and query the PostgreSQL database directly.
