from datetime import datetime
from typing import Dict
from src.servico.i_opecacoes_banco import IOperacoesBanco
from src.servico.i_servico_api import IServicoAPI
from pymssql.exceptions import IntegrityError, DatabaseError  # type: ignore
import re
import json
import pytz


class ETL:
    def __init__(self, api_legislacao: IServicoAPI, operacoes_banco: IOperacoesBanco):
        self.__api_legislacao = api_legislacao
        self.__operacoes_banco = operacoes_banco

    def __realizar_tratamento_etl_proposicao(self, proposicao: Dict):
        try:
            assunto = re.sub(r'[^\w\s.,;]', '',
                             proposicao['assunto']).strip().replace('\n', '')
            assunto = proposicao['assunto']
            assunto = " ".join(assunto.splitlines())
            assunto = assunto.encode('latin1').decode('utf-8')

        except:
            assunto = " ".join(assunto.split())
        data_registro = self.__obter_data_registro()
        numero = proposicao['numero'].strip()
        autor = " ".join(proposicao['autor'].encode(
                'latin1').decode('utf-8').strip().split())
        data_presentacao = proposicao['dataPublicacao']

        regime = proposicao['regime'].encode(
            'latin1').decode('utf-8').strip()

        situacao = proposicao['situacao'].encode(
            'latin1').decode('utf-8').strip()

        tipo_proposicao = proposicao['siglaTipoProjeto'].encode(
            'latin1').decode('utf-8').strip()

        ano = proposicao['ano']

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
            parametros_sql_consulta: str,
            colunas: str,
            dados: str,
            tabela: str,
            proposicao: Dict,
            url: str
    ):
        try:
            if self.__operacoes_banco.consultar_banco_id(sql=sql, parametros=parametros_sql_consulta) is None:
                placeholders = ", ".join(
                    [f"%({coluna})s" for coluna in dados.keys()])
                sql_banco = f"""
                            INSERT INTO {tabela} ({colunas})
                            VALUES ({placeholders})
                        """

            else:
                campos = ', '.join(
                    [f'{coluna} = %({coluna})s' for coluna in dados.keys()])

                sql_banco = f"""
                            UPDATE {tabela}
                            SET {campos}
                            WHERE NUMERO = {proposicao['numero'].strip()}
                        """

            self.__operacoes_banco.realizar_operacao_banco(
                consulta=sql_banco, parametros=dados)
        except KeyError as msg:

            mensagem_erro = f'Não encontrou a chave KeyError: {msg}'
            self.__registrar_erro(
                json_xml=proposicao,
                numero=proposicao['numero'].strip(),
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url
            )

        except IntegrityError as msg:

            mensagem_erro = f'Já existe a chave, {proposicao['numero'].strip()}'
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
                numero=proposicao['numero'].strip(),
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url)

        except Exception as msg:

            mensagem_erro = f'Erro fatal: {msg}'
            self.__registrar_erro(
                json_xml=proposicao,
                numero=proposicao['numero'].strip(),
                data_registro=self.__obter_data_registro(),
                mensagem_erro=mensagem_erro,
                url_api=url
            )

    def realizar_etl_propicao(self):
        for proposicao, url in self.__api_legislacao.obter_proposicoes():

            print(proposicao, url)

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

            parametros_sql_consulta = {
                'NUMERO': proposicao['numero'].strip()}
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
                url=url
            )

    def __realizar_tatamento_etl_tramitacao(self, tramitacao: Dict, dados: Dict):
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
        numero = dados['numero'].strip()
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
                dados_tramitacao, sql, parametros_sql_consulta = self.__realizar_tatamento_etl_tramitacao(
                    tramitacao=tramitacao, dados=dados)
                colunas = ", ".join(dados_tramitacao.keys())
                tabela = "tramitacao"
                self.__insercao_regisro(
                    sql=sql,
                    parametros_sql_consulta=parametros_sql_consulta,
                    colunas=colunas,
                    dados=dados,
                    proposicao=tramitacao,
                    tabela=tabela,
                    url=url
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
                parametros_sql_consulta = {
                    'NUMERO': proposicao['numero'].strip()}
                dados = self.__realizar_tratamento_etl_proposicao(
                    proposicao=proposicao
                )
                colunas = ", ".join(dados.keys())
                tabela = "proposicao"
                print('*' * 100)
                print(resultado[0])
                print(parametros_sql_consulta)
                print(colunas)
                print(tabela)
                print(dados)
                print('*' * 100)
                # self.__insercao_regisro(
                #     sql=sql,
                #     parametros_sql_consulta=parametros_sql_consulta,
                #     colunas=colunas,
                #     dados=dados,
                #     proposicao=proposicao,
                #     tabela=tabela,
                #     url=url
                # )

    def realizar_reprocesso_tramitacao(self):
        sql = """
            SELECT DISTINCT NUMERO
            FROM [dag_error]
        """
        resultados = self.__operacoes_banco.consultar_todos_registros(
            sql=sql, parametros=None)
        for resultado in resultados:
            for proposicao, url in self.__api_legislacao.obter_proposicoes(numero=resultado[0]):
                print(proposicao, url)
                self.__registrar_log(
                    json_xml=proposicao,
                    url_api=url,
                    mensagem_log='REALIZANDO CONSULTA PROPOSIÇÂO REPROCESSO'
                )
                dados = self.realizar_etl_propicao()

    def __obter_data_registro(self) -> str:
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_registro = datetime.now()
        data_registro = data_registro.astimezone(
            brasilia_tz).strftime('%Y-%m-%d %H:%M:%S')
        return data_registro

    def __registrar_erro(self, json_xml: str, numero: str, data_registro, mensagem_erro: str, url_api: str):
        json_xml = json.dumps(json_xml)
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
