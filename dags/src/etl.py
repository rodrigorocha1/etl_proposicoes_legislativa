from datetime import datetime
from typing import Any, Dict, Optional
from src.servico.i_opecacoes_banco import IOperacoesBanco
from src.servico.i_servico_api import IServicoAPI
from pymssql.exceptions import IntegrityError, DatabaseError  # type: ignore
import re
import json
import pytz


class ETL:
    def __init__(self, api_legislacao: IServicoAPI, operacoes_banco: IOperacoesBanco):
        """init

        Args:
            api_legislacao (IServicoAPI): servicço api
            operacoes_banco (IOperacoesBanco): serviço operações banco
        """
        self.__api_legislacao = api_legislacao
        self.__operacoes_banco = operacoes_banco

    def __realizar_tratamento_etl_proposicao(self, proposicao: Dict):
        """Método para realizar tatamento de proposição

        Args:
            proposicao (Dict): requisição da API
        """
        try:
            assunto = proposicao.get('assunto', '').strip()
            assunto = re.sub(r'[^\w\s.,;]', '', assunto)
            assunto = " ".join(assunto.splitlines())  # Remove quebras de linha
            assunto = assunto.encode(
                'latin1', 'ignore').decode('utf-8', 'ignore')

        except Exception:
            assunto = proposicao.get('assunto', '').strip()

        data_registro = self.__obter_data_registro()
        data_presentacao = proposicao.get('dataPublicacao', '').strip()
        numero = proposicao.get('numero', '').strip()
        autor = proposicao.get('autor', '').strip()
        regime = proposicao.get('regime', '').strip()
        situacao = proposicao.get('situacao', '').strip()
        tipo_proposicao = proposicao.get('siglaTipoProjeto', '').strip()
        ano = proposicao.get('ano', '')

        dados = {
            'AUTOR': autor,
            'DATA_PRESENTACAO': data_presentacao,
            'EMENTA': assunto.strip(),
            'REGIME': regime,
            'SITUACCAO': situacao,
            'TIPO_PROPOSICAO': tipo_proposicao,
            'NUMERO': numero,
            'ANO': ano,
            'CIDADE': 'Belo Horizonte',
            'ESTADO': 'Minas Gerais',
            'DATA_ATUALIZACAO_REGISTRO': data_registro
        }
        return dados

    def __insercao_regisro(
            self,
            sql: str,
            parametros_sql_consulta: Dict[str, Any],
            colunas: str,
            dados: Dict[str, Any],
            tabela: str,
            proposicao: Dict[str, Any],
            url: str,
            numero: str,
            flag: bool = True,
            valores_atualizacao: Optional[Dict[str, Any]] = None

    ):
        """_summary_

        Args:
            sql (str): Consulta sql 
            parametros_sql_consulta (Dict[str, Any]): parametros da consulta 
            colunas (str): colunas da tabela
            dados (Dict[str, Any]): dados que vai ser enviado a tabela
            tabela (str): nome da tabela
            proposicao (Dict[str, Any]): requisição da api
            url (str): url da api
            numero (str): numero da proposicao
            flag (bool, optional): flag de inserção . Defaults to True.

        """
        try:
            if self.__operacoes_banco.consultar_banco_id(sql=sql, parametros=parametros_sql_consulta) is None or flag:
                placeholders = ", ".join(
                    [f"%({coluna})s" for coluna in dados.keys()])
                sql_banco = f"""
                            INSERT INTO {tabela} ({colunas})
                            VALUES ({placeholders})
                        """

            else:
                campos = ', '.join(
                    [f'{coluna} = %({coluna})s' for coluna in dados.keys()])

                if valores_atualizacao:
                    valores = ', '.join(
                        [f'{campo_atualizacao} = %({campo_atualizacao})s' for campo_atualizacao in valores_atualizacao.keys(
                        )]
                    )

                else:
                    valores = ''

                sql_banco = f"""
                            UPDATE {tabela}
                            SET {campos}
                            WHERE {valores}
                        """

            self.__operacoes_banco.realizar_operacao_banco(
                consulta=sql_banco, parametros=dados)

        except KeyError as msg:

            mensagem_erro = f'Não encontrou a chave KeyError: {msg}'
            self.__registrar_erro(
                json_xml=proposicao,
                numero=numero,
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url
            )

        except IntegrityError as msg:

            mensagem_erro = f'Já existe a chave, {numero}'
            self.__registrar_log(
                json_xml=proposicao,
                mensagem_log=mensagem_erro,
                url_api=url
            )

        except DatabaseError as msg:

            # mensagem_erro = f'Dados invalidos em {str(msg.args[1]).split(', ')[1]}'
            mensagem_erro = f'Erro ao executar operação: {msg}'
            self.__registrar_erro(
                json_xml=proposicao,
                numero=numero,
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url)

        except Exception as msg:

            mensagem_erro = f'Erro fatal: {msg}'
            self.__registrar_erro(
                json_xml=proposicao,
                numero=numero,
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url
            )

    def realizar_etl_propicao(self):
        for proposicao, url in self.__api_legislacao.obter_proposicoes():
            self.__registrar_log(
                json_xml=proposicao,
                url_api=url,
                mensagem_log='REALIZANDO CONSULTA PROPOSIÇÂO'
            )
            sql = """
                    SELECT ID
                    FROM proposicao
                    WHERE NUMERO = %(NUMERO)s;
                """
            numero = proposicao['numero'].strip()
            parametros_sql_consulta = {
                'NUMERO': numero}
            dados = self.__realizar_tratamento_etl_proposicao(
                proposicao=proposicao
            )
            colunas = ", ".join(dados.keys())
            tabela = "proposicao"
            chave_atualizacao = {
                'NUMERO': numero
            }
            self.__insercao_regisro(
                sql=sql,
                parametros_sql_consulta=parametros_sql_consulta,
                colunas=colunas,
                dados=dados,
                proposicao=proposicao,
                tabela=tabela,
                url=url,
                flag=False,
                numero=numero,
                valores_atualizacao=chave_atualizacao

            )

    def __realizar_tatamento_etl_tramitacao(self, tramitacao: Dict, dados: Optional[Dict] = None, numero: Optional[str] = None):
        data = tramitacao['data'].encode(
            'latin1').decode('utf-8').strip()
        historico = tramitacao['historico'].encode(
            'latin1').decode('utf-8').strip()

        local = tramitacao['local'].encode(
            'latin1').decode('utf-8').strip()
        sql = """
                        SELECT ID
                        FROM tramitacao
                        WHERE ID_PROPOSICAO = %(ID_PROPOSICAO)s;
                    """

        parametros_sql_consulta = {
            'ID_PROPOSICAO': numero}
        data_registro = self.__obter_data_registro()

        dados_tramitacao = {
            'DESCRICAO': ' '.join(historico.splitlines()),
            'LOCAL_PROPOSICAO': local,
            'ID_PROPOSICAO': numero,
            'DATA_CRIACAO_TRAMITACAO': data,
            'DATA_ATUALIZACAO_REGISTRO': data_registro
        }
        return dados_tramitacao, sql, parametros_sql_consulta

    def realizar_etl_tramitacao(self):
        for dados, url in self.__api_legislacao.obter_proposicoes():
            for tramitacao in dados['listaHistoricoTramitacoes']:

                sql = """
                        SELECT ID
                        FROM tramitacao
                        WHERE ID_PROPOSICAO = %(ID_PROPOSICAO)s;
                    """
                numero = dados['numero'].strip()
                parametros_sql_consulta = {
                    'ID_PROPOSICAO': numero}
                dados_tramitacao, sql_tramitacao, parametros_sql_consulta = self.__realizar_tatamento_etl_tramitacao(
                    tramitacao=tramitacao, dados=dados, numero=numero)
                colunas = ", ".join(dados_tramitacao.keys())
                tabela = "tramitacao"
                chave_atualizacao = {
                    'ID_PROPOSICAO': numero
                }

                self.__insercao_regisro(
                    sql=sql_tramitacao,
                    parametros_sql_consulta=parametros_sql_consulta,
                    colunas=colunas,
                    dados=dados_tramitacao,
                    proposicao=dados,
                    tabela=tabela,
                    url=url,
                    flag=True,
                    numero=numero,
                    valores_atualizacao=chave_atualizacao

                )

    def realizar_reprocesso_proposicao(self):
        sql = """
            SELECT DISTINCT NUMERO
            FROM [dag_error]
        """

        resultados = self.__operacoes_banco.consultar_todos_registros(
            sql=sql, parametros=None)
        print(f'Resultados: {resultados}')
        for resultado in resultados:
            for proposicao, url in self.__api_legislacao.obter_proposicoes(numero=resultado[0]):

                self.__registrar_log(
                    json_xml=proposicao,
                    url_api=url,
                    mensagem_log='REALIZANDO CONSULTA PROPOSIÇÂO REPROCESSO'
                )
                numero = proposicao['numero'].strip()
                parametros_sql_consulta = {
                    'NUMERO': numero}
                dados = self.__realizar_tratamento_etl_proposicao(
                    proposicao=proposicao
                )
                colunas = ", ".join(dados.keys())
                tabela = "proposicao"

                self.__insercao_regisro(
                    sql=sql,
                    parametros_sql_consulta=parametros_sql_consulta,
                    colunas=colunas,
                    dados=dados,
                    proposicao=proposicao,
                    tabela=tabela,
                    url=url,
                    numero=numero
                )

    def realizar_reprocesso_tramitacao(self):
        sql = """
            SELECT DISTINCT NUMERO
            FROM [dag_error]
        """
        resultados = self.__operacoes_banco.consultar_todos_registros(
            sql=sql, parametros=None)
        for resultado in resultados:

            for proposicao, url in self.__api_legislacao.obter_proposicoes(numero=resultado[0]):
                for tramitacao in proposicao['listaHistoricoTramitacoes']:

                    self.__registrar_log(
                        json_xml=proposicao,
                        url_api=url,
                        mensagem_log='REALIZANDO CONSULTA PROPOSIÇÂO REPROCESSO'
                    )

                    dados_tramitacao, sql, parametros_sql_consulta = self.__realizar_tatamento_etl_tramitacao(
                        dados=proposicao, tramitacao=tramitacao, numero=resultado[0])

                    colunas = ", ".join(dados_tramitacao.keys())
                    tabela = "tramitacao"

                    self.__insercao_regisro(
                        sql=sql,
                        parametros_sql_consulta=parametros_sql_consulta,
                        colunas=colunas,
                        dados=dados_tramitacao,
                        proposicao=proposicao,
                        tabela=tabela,
                        url=url,
                        flag=True,
                        numero=None
                    )

    def __obter_data_registro(self) -> str:
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_registro = datetime.now()
        data_formatada = data_registro.astimezone(
            brasilia_tz).strftime('%Y-%m-%d %H:%M:%S')
        return data_formatada

    def __registrar_erro(self, json_xml: Dict[str, Any], numero: str, data_registro, mensagem_erro: str, url_api: str):

        dados_erro = {
            'NUMERO': numero,
            'URL_API': url_api,
            'JSON_XML': json_xml,
            'MENSAGEM_ERRO': mensagem_erro,
            'DATA_ATUALIZACAO': data_registro
        }

        sql_erro = f"""
                    INSERT INTO dag_error (NUMERO, URL_API, JSON_XML, MENSAGEM_ERRO, DATA_ATUALIZACAO)
                    VALUES (%(NUMERO)s, %(URL_API)s ,%(JSON_XML)s, %(MENSAGEM_ERRO)s, %(DATA_ATUALIZACAO)s)
                """
        self.__operacoes_banco.realizar_operacao_banco(
            consulta=sql_erro,
            parametros=dados_erro
        )

    def __registrar_log(self, json_xml: Dict, mensagem_log: str, url_api: str):
        dados_info = {
            'TIPO_LOG': 'INFO',
            'URL_API': url_api,
            'MENSAGEM_LOG': mensagem_log,
            'JSON_XML': json.dumps(json_xml)
        }

        sql_info = f"""
                    INSERT INTO log_dag (TIPO_LOG, URL_API, MENSAGEM_LOG, JSON_XML)
                    VALUES (%(TIPO_LOG)s, %(URL_API)s , %(MENSAGEM_LOG)s, %(JSON_XML)s )
                """
        self.__operacoes_banco.realizar_operacao_banco(
            consulta=sql_info,
            parametros=dados_info,


        )
