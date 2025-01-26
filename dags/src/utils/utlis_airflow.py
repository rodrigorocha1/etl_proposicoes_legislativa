from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from typing import Dict
from src.servico.opercacoes_banco import OperacaoBanco


def inserir_registro_log(task_id: str, parametros: Dict, sql: str, **kwargs,):
    task_instance = kwargs['ti']

    result = task_instance.xcom_pull(task_ids=task_id)
    print('=' * 9)
    print(kwargs)
    print(task_instance)
    print(result)


def verificar_registros_log_error(tarefa_a: str, tarefa_b: str):
    """Método para decisão de tarefa

    Args:
        tarefa_a (str): tarefa se for verdadeira
        tarefa_b (str): tarefa se for falsa

    Returns:
        _type_: _description_
    """

    sql = """
    SELECT  NUMERO
    FROM [dag_error]

    """

    ob = OperacaoBanco()
    resultado = ob.consultar_banco_id(sql=sql, parametros=None)

    if resultado is not None:
        print(f'Resultado dentro do none: {resultado}')
        return tarefa_a
    print(f'Resultado fora do none: {resultado}')
    return tarefa_b
