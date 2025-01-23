from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from src.servico.opercacoes_banco import MsSqlHook


class OperacaoBanco:
    def __init__(self):
        self.__id_conexao_mssql = 'sql_server_airflow'
        self.__mssql_hook = MsSqlHook(mssql_conn_id=self.__id_conexao_mssql)

    def realizar_operacao_banco(self, consulta: str):
        """Método para realizar operações no banco

        Args:
            consulta (str): _description_
        """
        self.__mssql_hook.run(sql=consulta)
