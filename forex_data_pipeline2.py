from airflow import DAG
from datetime import datetime,timedelta
from airflow.sensors.http_sensor import HttpSensor
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.operators.python_operator import PythonOperator
import json
import csv
import requests

default_args = {
      "owner" : "airflow",
      "start_date": datetime(2019,12,4),
      "depends_on_past": False,
      "email_on_failure": False,
      "email_on_retry": False,
      "email": "rodns01@gmail.com",
      "retries": 1,
      "retries_delay": timedelta(minutes=5)
 }
def download_rates():
    with open('/usr/local/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for row in reader:
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get('https://api.exchangeratesapi.io/latest?base=' + base).json()
            outdata = {'base': base, 'rates': {}, 'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/usr/local/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')


with DAG(dag_id="forex_data_pipeline",
        schedule_interval="@daily",
        default_args=default_args,
        catchup= False) as dag:
    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        method= 'GET',
        http_con_id='forex_api',
        endpoint='',
        response_check= lambda response: "rates" in response.text,
        poke_interval= 5,
        timeout= 20
    )
    is_forex_currencies_file_available = FileSensor(
        task_id= "is_forex_currencies_file_available",
        poke_interval= 5,
        fs_conn_id= 'forex_path',
        filepath= 'forex_currencies.csv',
        timeout= 20
    )
    downloading_rates  = PythonOperator(
        task_id='downloading_rates',
        python_callable=download_rates,
        #op_args=[]
    )