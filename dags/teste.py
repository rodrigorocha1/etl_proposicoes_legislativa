from airflow import DAG
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    dag_id='example_mssql_operator',

    default_args=default_args,
    description='Example DAG for MSSQLOperator',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    create_table = MsSqlOperator(
        task_id='create_table',
        mssql_conn_id='sql_server_airflow',
        sql="""
        SELECT GETDATE();


        """,
        do_xcom_push=True,

    )

    create_table
