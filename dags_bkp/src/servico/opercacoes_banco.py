from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from typing import Any, Dict, Optional
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

    def consultar_banco_id(self, sql: str, parametros: Dict[str, Any]) -> Optional[str]:
        resultado = self.__mssql_hook.get_first(sql=sql, parameters=parametros)
        return str(resultado[0]) if resultado is not None else resultado

    def consultar_todos_registros(self, sql: str, parametros: Dict[str, Any]):
        """Consulta e retorna todos os registros do banco

        Args:
            sql (str): Consulta SQL a ser executada
            parametros (Dict[str, Any]): Parâmetros da consulta

        Returns:
            List[tuple]: Lista de tuplas com os resultados
        """
        resultados = self.__mssql_hook.get_records(
            sql=sql, parameters=parametros)
        return resultados
