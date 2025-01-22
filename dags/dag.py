from airflow import DAG
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.operators.empty import EmptyOperator
from datetime import datetime
from datetime import datetime, timedelta

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
        SELECT GETDATE();

        """,
        do_xcom_push=True,

    )

    checar_conexao_api = HttpSensor(
        task_id='checar_conexao_api_dados_abertos_mg',
        http_conn_id='api_dados_abertos_mg',
        endpoint='/ws/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ord=3&p=1&ini=20241201&fim=20241231',
        headers={"Content-Type": "application/json"},
        poke_interval=1,
        timeout=5,
        mode='poke',
        trigger_rule='one_success'
    )

    # falha_um = EmptyOperator(
    #     task_id='falha_um',
    #     trigger_rule='one_failed'
    # )

    sucesso = EmptyOperator(
        task_id='sucesso_dois',
        trigger_rule='one_success'
    )

    # falha_dois = EmptyOperator(
    #     task_id='falha_dois',
    #     trigger_rule='one_failed'
    # )

    inserir_mensagem_de_erro_conexao_banco = MsSqlOperator(
        task_id='id_inserir_mensagem_de_erro_conexao_banco',
        mssql_conn_id='sql_server_airflow',
        sql="""
        INSERT INTO controle_log (TIPO_LOG, DATA_ERRO, MENSAGEM_LOG)
        VALUES
        ('1', GETDATE(), 'ERRO na verificação da conexão do banco');

        """,

        trigger_rule='one_failed'

    )

    inserir_mensagem_de_erro_conexao_api = MsSqlOperator(
        task_id='id_inserir_mensagem_de_erro_conexao_api',
        mssql_conn_id='sql_server_airflow',
        sql="""
        INSERT INTO controle_log (TIPO_LOG, DATA_ERRO, MENSAGEM_LOG)
        VALUES
        ('1', GETDATE(), 'ERRO na verificação da conexão da API');

        """,

        trigger_rule='one_failed'

    )

    delete_log_tipo_1 = MsSqlOperator(
        task_id='id_delete_log_tipo_1',
        mssql_conn_id='sql_server_airflow',
        sql="""
        DELETE
        FROM controle_log
        WHERE TIPO_LOG = '1' ;

        """,

        trigger_rule='none_failed'

    )

    fim_dag = EmptyOperator(
        task_id='fim_dag',
        trigger_rule='dummy'
    )

    inicio_dag >> checar_conexao_banco
    checar_conexao_banco >> [checar_conexao_api,
                             inserir_mensagem_de_erro_conexao_banco]
    checar_conexao_api >> [
        sucesso, inserir_mensagem_de_erro_conexao_api] >> delete_log_tipo_1 >> fim_dag

    [sucesso, inserir_mensagem_de_erro_conexao_api] >> delete_log_tipo_1 >> fim_dag
    inserir_mensagem_de_erro_conexao_banco >> delete_log_tipo_1 >> fim_dag
