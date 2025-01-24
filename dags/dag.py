from src.servico.api_legislacao import APILegislacao
from src.servico.opercacoes_banco import OperacaoBanco
from airflow import DAG
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from airflow.operators.python import PythonOperator
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
    dag_id='ETL_PROPOSICOES_LEGISLATIVA',

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

    checar_conexao_banco = MsSqlOperator(
        task_id='checar_conexao_banco',
        mssql_conn_id='sql_server_airflow',
        sql="""
        SELECT getdate();

        """,
        do_xcom_push=True,

    )
    verificar_status = PythonOperator(
        task_id='verificar_status',
        python_callable=inserir_registro_log,
        op_args=[
            'checar_conexao_banco',
            {
                'TIPO_LOG': 'ERROR',
                'MENSAGEM_LOG': 'ERRO AO CONECTAR NO BANCO'
            },
            """
                INSERT INTO log_dag (TIPO_LOG, MENSAGEM_LOG)
                VALUES (%(TIPO_LOG)s, %(MENSAGEM_LOG)s)
            """
        ],

        trigger_rule='one_failed',

    )

    registrar_proxima_dag = PythonOperator(
        task_id='registrar_proxima_dag',
        python_callable=inserir_registro_log,
        op_args=[
            'registrar_proxima_dag',
            {
                'TIPO_LOG': 'INFO',
                'MENSAGEM_LOG': 'EXECUTAR DAG: checar_conexao_api_dados_abertos_mg'
            },
            """
                INSERT INTO log_dag (TIPO_LOG, MENSAGEM_LOG)
                VALUES (%(TIPO_LOG)s, %(MENSAGEM_LOG)s)
            """
        ],
        trigger_rule='one_success'
    )

    checar_conexao_api = HttpSensor(
        task_id='checar_conexao_api_dados_abertos_mg',
        http_conn_id='api_dados_abertos_mg',
        endpoint='/ws/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ord=3&p=1&ini=20241201&fim=20241231',
        headers={"Content-Type": "application/json"},
        poke_interval=1,
        timeout=5,
        mode='poke',

        trigger_rule='one_success',
    )

    # etl_registro_hora = PythonOperator(
    #     task_id='etl_registro_hora',
    #     python_callable=ETL(
    #         api_legislacao=APILegislacao(),
    #         operacoes_banco=OperacaoBanco()
    #     ).realizar_etl_propicao
    # )

    # falha_um = EmptyOperator(
    #     task_id='falha_um',
    #     trigger_rule='one_failed'
    # )

    # falha_dois = EmptyOperator(
    #     task_id='falha_dois',
    #     trigger_rule='one_failed'
    # )

    # inserir_mensagem_de_erro_conexao_banco = MsSqlOperator(
    #     task_id='id_inserir_mensagem_de_erro_conexao_banco',
    #     mssql_conn_id='sql_server_airflow',
    #     sql="""
    #         BEGIN TRY
    #             INSERT INTO controle_log (TIPO_LOG, DATA_ERRO, MENSAGEM_LOG)
    #             VALUES
    #             ('1-1', GETDATE(), 'ERRO na verificação da conexão da API');
    #         END TRY

    #         BEGIN CATCH
    #             UPDATE
    #             controle_log
    #             SET DATA_ERRO = GETDATE()
    #             WHERE TIPO_LOG = '1-1'

    #         END CATCH;

    #     """,

    #     trigger_rule='one_failed'

    # )

    # inserir_mensagem_de_erro_conexao_api = MsSqlOperator(
    #     task_id='id_inserir_mensagem_de_erro_conexao_api',
    #     mssql_conn_id='sql_server_airflow',
    #     sql="""
    #         BEGIN TRY
    #             INSERT INTO controle_log (TIPO_LOG, DATA_ERRO, MENSAGEM_LOG)
    #             VALUES
    #             ('1-1', GETDATE(), 'ERRO na verificação da conexão da API');
    #         END TRY

    #         BEGIN CATCH
    #             UPDATE
    #             controle_log
    #             SET DATA_ERRO = GETDATE()
    #             WHERE TIPO_LOG = '1-1'

    #         END CATCH;

    #     """,

    #     trigger_rule='one_failed'

    # )

    # delete_log_tipo_1 = MsSqlOperator(
    #     task_id='id_delete_log_tipo_1',
    #     mssql_conn_id='sql_server_airflow',
    #     sql="""
    #     DELETE
    #     FROM controle_log
    #     WHERE TIPO_LOG IN ('1-1', '1-2') ;

    #     """,

    #     trigger_rule='none_failed'

    # )

    fim_dag = EmptyOperator(
        task_id='fim_dag',
        trigger_rule='all_done'
    )

    inicio_dag >> checar_conexao_banco >> [
        registrar_proxima_dag, verificar_status]
    registrar_proxima_dag >> checar_conexao_api >> fim_dag
    verificar_status >> fim_dag

    # inicio_dag >> checar_conexao_banco
    # checar_conexao_banco >> [checar_conexao_api,
    #                          inserir_mensagem_de_erro_conexao_banco]
    # checar_conexao_api >> [
    #     etl_registro_hora, inserir_mensagem_de_erro_conexao_api] >> delete_log_tipo_1 >> fim_dag

    # [etl_registro_hora, inserir_mensagem_de_erro_conexao_api] >> delete_log_tipo_1 >> fim_dag
    # inserir_mensagem_de_erro_conexao_banco >> delete_log_tipo_1 >> fim_dag
