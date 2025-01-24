from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from typing import Dict

mssql_hook = MsSqlHook(mssql_conn_id='sql_server_airflow')


def inserir_registro_log(task_id: str, parametros: Dict, sql: str, **kwargs,):
    task_instance = kwargs['ti']

    result = task_instance.xcom_pull(task_ids=task_id)
    print(kwargs, task_instance, result)
    mssql_hook.run(sql=sql, parameters=parametros)
