from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook

from typing import Any, Dict
from src.servico.i_opecacoes_banco import IOperacoesBanco


class OperacaoBanco(IOperacoesBanco):
    def __init__(self):
        self.__id_conexao_mssql = 'sql_server_airflow'
        self.__mssql_hook = MsSqlHook(mssql_conn_id=self.__id_conexao_mssql)

    def realizar_operacao_banco(self, consulta: str, parametros: Dict[str, Any]):
        """Método para realizar operações no banco

        Args:
            consulta (str): _description_
        """
        self.__mssql_hook.run(sql=consulta, parameters=parametros)
