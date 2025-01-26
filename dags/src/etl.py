from datetime import datetime
from src.servico.i_opecacoes_banco import IOperacoesBanco
from src.servico.i_servico_api import IServicoAPI
from pymssql.exceptions import IntegrityError, DatabaseError
import re
import json
import pytz


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
                    parametros=dados_info,


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

                proposicao = json.dumps(proposicao)
                dados_erro = {
                    'NUMERO': numero,
                    'JSON_XML': proposicao,
                    'MENSAGEM_ERRO': f'Não encontrou a chave KeyError: {msg}',
                    'DATA_ATUALIZACAO': data_registro
                }

                sql_erro = f"""
                    INSERT INTO dag_error (NUMERO, JSON_XML, MENSAGEM_ERRO, DATA_ATUALIZACAO)
                    VALUES (%(NUMERO)s, %(JSON_XML)s, %(MENSAGEM_ERRO)s, %(DATA_ATUALIZACAO)s)
                """
                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_erro,
                    parametros=dados_erro
                )
            except IntegrityError as msg:

                proposicao = json.dumps(proposicao)
                dados_erro = {
                    'NUMERO': numero,
                    'JSON_XML': proposicao,
                    'MENSAGEM_ERRO': f'Já existe a chave, {numero}',
                    'DATA_ATUALIZACAO': data_registro
                }

                sql_erro = f"""
                    INSERT INTO dag_error (NUMERO, JSON_XML, MENSAGEM_ERRO, DATA_ATUALIZACAO)
                    VALUES (%(NUMERO)s, %(JSON_XML)s, %(MENSAGEM_ERRO)s, %(DATA_ATUALIZACAO)s)
                """
                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_erro,
                    parametros=dados_erro
                )

            except DatabaseError as msg:

                proposicao = json.dumps(proposicao)
                dados_erro = {
                    'NUMERO': numero,
                    'JSON_XML': proposicao,
                    'MENSAGEM_ERRO': f'Dados invalidos em {str(msg.args[1]).split(', ')[1]}',
                    'DATA_ATUALIZACAO': data_registro
                }

                sql_erro = f"""
                    INSERT INTO dag_error (NUMERO, JSON_XML, MENSAGEM_ERRO, DATA_ATUALIZACAO)
                    VALUES (%(NUMERO)s, %(JSON_XML)s, %(MENSAGEM_ERRO)s, %(DATA_ATUALIZACAO)s)
                """
                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_erro,
                    parametros=dados_erro
                )

            except Exception as msg:
                proposicao = json.dumps(proposicao)
                dados_erro = {
                    'NUMERO': numero,
                    'JSON_XML': proposicao,
                    'MENSAGEM_ERRO': f'Erro Fatal',
                    'DATA_ATUALIZACAO': data_registro
                }

                sql_erro = f"""
                    INSERT INTO dag_error (NUMERO, JSON_XML, MENSAGEM_ERRO, DATA_ATUALIZACAO)
                    VALUES (%(NUMERO)s, %(JSON_XML)s, %(MENSAGEM_ERRO)s, %(DATA_ATUALIZACAO)s)
                """
                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_erro,
                    parametros=dados_erro
                )
