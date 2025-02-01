from src.servico.api_legislacao import APILegislacao
from src.servico.opercacoes_banco import OperacaoBanco
from airflow import DAG
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
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
    'retry_delay': timedelta(seconds=5)
}

with DAG(
    dag_id='ETL_PROPOSICOES_LEGISLATIVA_TESTE_ERROR',

    default_args=default_args,
    description='DAG para extrair os dados da api ',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['ETL', 'Proposições', 'LEGISLAÇÃO', 'MINAS GERAIS'],

) as dag:

    inicio_dag = EmptyOperator(
        task_id='inicio_dag',
        trigger_rule='dummy'

    )

    # etl_reprocesso_proposicao = PythonOperator(
    #     task_id='etl_reprocesso_proposicao',
    #     python_callable=ETL(
    #         api_legislacao=APILegislacao(),
    #         operacoes_banco=OperacaoBanco()
    #     ).realizar_reprocesso_proposicao,

    # )
    etl_reprocesso_tramitacao = PythonOperator(
        task_id='etl_reprocesso_tramitacao',
        python_callable=ETL(
            api_legislacao=APILegislacao(),
            operacoes_banco=OperacaoBanco()
        ).realizar_reprocesso_tramitacao,

    )

    fim_dag = EmptyOperator(
        task_id='fim_dag',
        trigger_rule='all_done'
    )

    inicio_dag >> etl_reprocesso_tramitacao >> fim_dag
