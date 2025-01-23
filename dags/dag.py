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

    def log_api_connection_error(context):
        task_instance = context.get('task_instance', None)
        task_id = context.get('task_id', None)
        dag_id = context.get('dag', {}).get('dag_id', None)
        execution_date = context.get('execution_date', None)
        exception = context.get('exception', 'Erro desconhecido')
        try_number = context.get('try_number', 1)
        run_id = context.get('run_id', None)

        # Criando a mensagem de erro
        error_message = f"Task {task_id} do DAG {dag_id} falhou. Exceção: {exception}. Tentativa: {try_number}. Execução: {execution_date}. Run ID: {run_id}"
        print(error_message)
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
        endpoint='/w/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ord=3&p=1&ini=20241201&fim=20241231',
        headers={"Content-Type": "application/json"},
        poke_interval=1,
        timeout=5,
        mode='poke',
        trigger_rule='one_success',
        on_failure_callback=log_api_connection_error)

    etl_registro_hora = PythonOperator(
        task_id='etl_registro_hora',
        python_callable=ETL(
            api_legislacao=APILegislacao(),
            operacoes_banco=OperacaoBanco()
        ).realizar_etl_propicao
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
            BEGIN TRY
                INSERT INTO controle_log (TIPO_LOG, DATA_ERRO, MENSAGEM_LOG)
                VALUES
                ('1-1', GETDATE(), 'ERRO na verificação da conexão da API');
            END TRY

            BEGIN CATCH
                UPDATE 
                controle_log
                SET DATA_ERRO = GETDATE()
                WHERE TIPO_LOG = '1-1'

            END CATCH;

        """,

        trigger_rule='one_failed'

    )

    inserir_mensagem_de_erro_conexao_api = MsSqlOperator(
        task_id='id_inserir_mensagem_de_erro_conexao_api',
        mssql_conn_id='sql_server_airflow',
        sql="""
            BEGIN TRY
                INSERT INTO controle_log (TIPO_LOG, DATA_ERRO, MENSAGEM_LOG)
                VALUES
                ('1-1', GETDATE(), 'ERRO na verificação da conexão da API');
            END TRY

            BEGIN CATCH
                UPDATE 
                controle_log
                SET DATA_ERRO = GETDATE()
                WHERE TIPO_LOG = '1-1'

            END CATCH;


        """,

        trigger_rule='one_failed'

    )

    delete_log_tipo_1 = MsSqlOperator(
        task_id='id_delete_log_tipo_1',
        mssql_conn_id='sql_server_airflow',
        sql="""
        DELETE
        FROM controle_log
        WHERE TIPO_LOG IN ('1-1', '1-2') ;

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
        etl_registro_hora, inserir_mensagem_de_erro_conexao_api] >> delete_log_tipo_1 >> fim_dag

    [etl_registro_hora, inserir_mensagem_de_erro_conexao_api] >> delete_log_tipo_1 >> fim_dag
    inserir_mensagem_de_erro_conexao_banco >> delete_log_tipo_1 >> fim_dag
