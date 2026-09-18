from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from extraction.cities import extract_cities
from extraction.weather import extract_weather

from transformation.cleaning import clean_data
from transformation.validation import validate_data
from transformation.features import calculate_risks

from load.postgres import load_data


with DAG(
    dag_id="weather_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    extract_cities_task = PythonOperator(
        task_id="extract_cities",
        python_callable=extract_cities,
    )

    extract_weather_task = PythonOperator(
        task_id="extract_weather",
        python_callable=extract_weather,
    )

    clean_data_task = PythonOperator(
        task_id="clean_data",
        python_callable=clean_data,
    )

    validate_data_task = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
    )

    calculate_risks_task = PythonOperator(
        task_id="calculate_risks",
        python_callable=calculate_risks,
    )

    load_data_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    extract_cities_task >> extract_weather_task
    extract_weather_task >> clean_data_task
    clean_data_task >> validate_data_task
    validate_data_task >> calculate_risks_task
    calculate_risks_task >> load_data_task