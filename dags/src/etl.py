from src.servico.api_legislacao import APILegislacao
from src.servico.i_opecacoes_banco import IOperacoesBanco
from src.servico.i_servico_api import IServicoAPI
import re
import json


class ETL:
    def __init__(self, api_legislacao: IServicoAPI, operacoes_banco: IOperacoesBanco):
        self.__api_legislacao = api_legislacao
        self.__operacoes_banco = operacoes_banco

    def realizar_etl_propicao(self):
        for proposicao in self.__api_legislacao.obter_proposicoes():
            try:

                dados_info = {
                    'TIPO_LOG': 'INFO',
                    'MENSAGEM_LOG': 'OBTENÇÃO RESULTADO',
                    'JSON_XML': json.dumps(proposicao)
                }

                sql_info = f"""
                    INSERT INTO log_dag (TIPO_LOG, MENSAGEM_LOG, JSON_XML)
                    VALUES (%(TIPO_LOG)s, %(MENSAGEM_LOG)s, %(JSON_XML)s )
                """
                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_info,
                    parametros=dados_info
                )
                try:
                    assunto = re.sub(r'[^\w\s.,;]', '',
                                     proposicao['assunto']).strip().replace('\n', '')
                    assunto = proposicao['assunto']
                    assunto = assunto.encode('latin1').decode('utf-8')

                except:
                    assunto = " ".join(assunto.split())

                dado = {
                    'AUTOR': " ".join(proposicao['autor'].split()).encode('latin1').decode('utf-8'),
                    'DATA_PRESENTACAO': proposicao['dataPublicacao'],
                    'EMENTA': assunto,
                    'REGIME': proposicao['regime'].encode('latin1').decode('utf-8'),
                    'SITUACCAO': proposicao['situacao'].encode('latin1').decode('utf-8'),
                    'TIPO_PROPOSICAO': proposicao['siglaTipoProjeto'].encode('latin1').decode('utf-8'),
                    'NUMERO': proposicao['numero'],
                    'ANO': proposicao['ano'],
                    'CIDADE': 'Belo Horizonte',
                    'ESTADO': 'Minas Gerais'
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

                proposicao = json.dumps(proposicao)
                dados_erro = {
                    'TIPO_LOG': 'ERROR',
                    'MENSAGEM_LOG': f'Não encontrou a chave: {msg}',
                    'JSON_XML': proposicao

                }

                sql_erro = f"""
                    INSERT INTO log_dag (TIPO_LOG, MENSAGEM_LOG, JSON_XML)
                    VALUES (%(TIPO_LOG)s, %(MENSAGEM_LOG)s, %(JSON_XML)s )
                """
                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_erro,
                    parametros=dados_erro
                )
            except Exception as msg:

                proposicao = json.dumps(proposicao)
                dados_erro = {
                    'TIPO_LOG': 'CRITICAL',
                    'MENSAGEM_LOG': f'ERRO FATAL: {msg}',
                    'JSON_XML': proposicao

                }
                print('*' * 20)
                print(dados_erro)

                sql_erro = f"""
                    INSERT INTO log_dag (TIPO_LOG, MENSAGEM_LOG, JSON_XML)
                    VALUES (%(TIPO_LOG)s, %(MENSAGEM_LOG)s, %(JSON_XML)s )
                """
                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_erro,
                    parametros=dados_erro
                )
