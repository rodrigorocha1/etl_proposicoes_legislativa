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

    def realizar_etl_propicao(self):
        for proposicao, url in self.__api_legislacao.obter_proposicoes():
            try:

                self.__registrar_log(
                    json_xml=proposicao,
                    url_api=url,
                    mensagem_log='REALIZANDO CONSULTA PROPOSIÇÂO'
                )
                try:
                    assunto = re.sub(r'[^\w\s.,;]', '',
                                     proposicao['assunto']).strip().replace('\n', '')
                    assunto = proposicao['assunto']
                    assunto = " ".join(assunto.splitlines())
                    assunto = assunto.encode('latin1').decode('utf-8')

                except:
                    assunto = " ".join(assunto.split())

                brasilia_tz = pytz.timezone('America/Sao_Paulo')
                data_registro = datetime.now()
                data_registro = data_registro.astimezone(
                    brasilia_tz).strftime('%Y-%m-%d %H:%M:%S')

                autor = " ".join(proposicao['autor'].encode(
                    'latin1').decode('utf-8').strip().split())
                data_presentacao = proposicao['dataPublicacao']

                regime = proposicao['regime'].encode(
                    'latin1').decode('utf-8').strip()

                situacao = proposicao['situacao'].encode(
                    'latin1').decode('utf-8').strip()

                tipo_proposicao = proposicao['siglaTipoProjeto'].encode(
                    'latin1').decode('utf-8').strip()

                numero = proposicao['numero'].strip()

                ano = proposicao['ano']

                dado = {
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
                colunas = ", ".join(dado.keys())
                placeholders = ", ".join(
                    [f"%({coluna})s" for coluna in dado.keys()])  # Correção aqui

                tabela = "proposicao"
                sql_insersao = f"""
                        INSERT INTO {tabela} ({colunas})
                        VALUES ({placeholders})
                    """

                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_insersao, parametros=dado)
            except KeyError as msg:

                mensagem_erro = f'Não encontrou a chave KeyError: {msg}'
                self.__registrar_erro(
                    json_xml=proposicao,
                    numero=numero,
                    data_registro=data_registro,
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
                    data_registro=data_registro,
                    mensagem_erro=mensagem_erro,
                    url_api=url)

            except Exception as msg:

                mensagem_erro = f'Erro fatal: {msg}'
                self.__registrar_erro(
                    json_xml=proposicao,
                    numero=numero,
                    data_registro=data_registro,
                    mensagem_erro=mensagem_erro,
                    url_api=url
                )

    def realizar_etl_tramitacao(self):
        for dados, url in self.__api_legislacao.obter_proposicoes():
            for tramitacao in dados['listaHistoricoTramitacoes']:
                data = tramitacao['data'].encode(
                    'latin1').decode('utf-8').strip()
                historico = tramitacao['historico'].encode(
                    'latin1').decode('utf-8').strip()
                local = tramitacao['local'].encode(
                    'latin1').decode('utf-8').strip()

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
