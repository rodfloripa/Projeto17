from airflow import DAG
from datetime import datetime,timedelta
from airflow.sensors.http_sensor import HttpSensor

default_args = {
      "owner" : "airflow",
      "start_date": datetime(2019,12,4),
      "depends_on_past": False,
      "email_on_failure": False,
      "email_on_retry": False,
      "email": "rodns01@gmail.com"
      "retries": 1,
      "retries_delay": timedelta(minutes=5)
 }

with DAG(dag_id="forex_data_pipeline",
 	     schedule_interval="@daily",
 	     default_args=default_args,
 	     cathup= False) as dag:
 	is_forex_rates_available = HttpSensor(
 		task_id="is_forex_rates_available"
        method= 'GET',
        http_con_id='forex_api',
        endpoint= 'latest',
        response_check= lambda response: "rates" in response.text
        poke_interval= 5,
        timeout= 20
 	)