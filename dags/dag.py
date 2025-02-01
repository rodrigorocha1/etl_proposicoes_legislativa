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

    etl_registro_proposicao = PythonOperator(
        task_id='etl_registro_proposicao',
        python_callable=ETL(
            api_legislacao=APILegislacao(),
            operacoes_banco=OperacaoBanco()
        ).realizar_etl_propicao
    )

    etl_registro_tramitacao = PythonOperator(
        task_id='etl_registro_tramitacao',
        python_callable=ETL(
            api_legislacao=APILegislacao(),
            operacoes_banco=OperacaoBanco()
        ).realizar_etl_tramitacao
    )

    etl_reprocesso_proposicao = PythonOperator(
        task_id='etl_reprocesso_proposicao',
        python_callable=ETL(
            api_legislacao=APILegislacao(),
            operacoes_banco=OperacaoBanco()
        ).realizar_reprocesso_proposicao,

    )

    etl_reprocesso_tramitacao = PythonOperator(
        task_id='etl_reprocesso_tramitacao',
        python_callable=ETL(
            api_legislacao=APILegislacao(),
            operacoes_banco=OperacaoBanco()
        ).realizar_reprocesso_tramitacao,

    )

    etl_decisao_tarefa = BranchPythonOperator(
        task_id='etl_decisao_tarefa',
        python_callable=verificar_registros_log_error,
        op_args=('etl_reprocesso_proposicao', 'sem_dados_reprocessameto')

    )

    sem_dados_reprocessar = EmptyOperator(
        task_id='sem_dados_reprocessameto'
    )

    falha_um = EmptyOperator(
        task_id='falha_um',
        trigger_rule='one_failed'
    )

    fim_dag = EmptyOperator(
        task_id='fim_dag',
        trigger_rule='all_done'
    )

    etl_deletar_registro_depara = MsSqlOperator(
        task_id='etl_deletar_registro_depara',
        mssql_conn_id='sql_server_airflow',
        sql="""
        
        DECLARE @NUMERO INT;

        DECLARE numeros_cursor CURSOR FOR
        SELECT DISTINCT dg_error.NUMERO
        FROM proposicao pro 
        INNER JOIN dag_error dg_error ON pro.NUMERO = dg_error.NUMERO;


        OPEN numeros_cursor;
        FETCH NEXT FROM numeros_cursor INTO @NUMERO;


        WHILE @@FETCH_STATUS = 0
        BEGIN

            DELETE 
            FROM dag_error
            WHERE ID = @NUMERO;


            FETCH NEXT FROM numeros_cursor INTO @NUMERO;
        END

        -- Fechar e desalocar o cursor
        CLOSE numeros_cursor;
        DEALLOCATE numeros_cursor;


        """,

    )

    inicio_dag >> checar_conexao_banco >> [
        checar_conexao_api, verificar_status]

    checar_conexao_api >> [etl_registro_proposicao, falha_um]

    etl_registro_proposicao >> etl_registro_tramitacao

    etl_registro_tramitacao >> etl_decisao_tarefa >> [
        etl_reprocesso_proposicao, sem_dados_reprocessar]

    sem_dados_reprocessar >> fim_dag

    etl_reprocesso_proposicao >> etl_reprocesso_tramitacao >> etl_deletar_registro_depara >> fim_dag

    falha_um >> fim_dag

    verificar_status >> fim_dag
