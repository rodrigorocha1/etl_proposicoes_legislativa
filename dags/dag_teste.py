import pytz
from src.servico.api_legislacao import APILegislacao
from src.servico.opercacoes_banco import OperacaoBanco
from airflow import DAG
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.operators.empty import EmptyOperator
from datetime import datetime
from datetime import datetime, timedelta
from src.etl import ETL
from src.utils.utlis_airflow import *

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
    'execution_timeout': timedelta(seconds=60),
}

with DAG(
    dag_id='DAG_TESTE',

    default_args=default_args,
    description='DAG TESTE',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['DAG', 'TESTE'],

) as dag:

    def exibir_hora():
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_registro = datetime.now()
        print(data_registro.strftime('%Y-%m-%d %H:%M:%S.%f%z'))

        data_registro = data_registro.astimezone(brasilia_tz)
        print(data_registro.strftime('%Y-%m-%d %H:%M:%S.%f%z'))

    def consultar_banco():
        mssql_hook = MsSqlHook(mssql_conn_id='sql_server_airflow')
        sql = """
            SELECT ID
            FROM proposicao
            WHERE NUMERO = '11017';
        """
        resultado = mssql_hook.get_first(sql=sql)
        print(resultado[0] if resultado is not None else resultado)

    inicio_dag = EmptyOperator(
        task_id='inicio_dag',
        trigger_rule='dummy'

    )

    tarefa_a = EmptyOperator(
        task_id='tarefa_a',



    )
    tarefa_b = EmptyOperator(
        task_id='tarefa_b',


    )
    teste_a = PythonOperator(
        task_id='etl_decisao_tarefa',
        python_callable=consultar_banco,

    )

    teste_consulta = BranchPythonOperator(
        task_id='etl_decisao_tarefa',
        python_callable=verificar_registros_log_error,
        op_args=('tarefa_a', 'tarefa_b')
    )

    fim_dag = EmptyOperator(
        task_id='fim_dag',
        trigger_rule='dummy'

    )

    inicio_dag >> teste_consulta >> [tarefa_a, tarefa_b] >> fim_dag
