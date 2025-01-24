from src.servico.api_legislacao import APILegislacao
from src.servico.i_opecacoes_banco import IOperacoesBanco
from src.servico.i_servico_api import IServicoAPI
import re


class ETL:
    def __init__(self, api_legislacao: IServicoAPI, operacoes_banco: IOperacoesBanco):
        self.__api_legislacao = api_legislacao
        self.__operacoes_banco = operacoes_banco

    def realizar_etl_propicao(self):
        for proposicao in self.__api_legislacao.obter_proposicoes():
            try:
                assunto = re.sub(r'[^\w\s.,;]', '',
                                 proposicao['assunto']).strip().replace('\n', '')
                dado = {
                    'AUTOR': proposicao['autor'],
                    'DATA_PRESENTACAO': proposicao['dataPublicacao'],
                    'EMENTA': assunto,
                    'REGIME': proposicao['regime'],
                    'SITUACCAO': proposicao['situacao'],
                    'TIPO_PROPOSICAO': proposicao['siglaTipoProjeto'],
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
            except Exception as msg:
                print(msg)
                dados_erro = {
                    'TIPO_LOG': 'ERROR',
                    'MENSAGEM_ERRO': str(msg),
                    'JSON_XML': proposicao

                }

                sql_erro = f"""
                    INSERT INTO log_dag (TIPO_LOG, MENSAGEM_ERRO, JSON_XML)
                    VALUES (%(TIPO_LOG)s, %(MENSAGEM_ERRO)s, %(JSON_XML)s )
                """
                self.__operacoes_banco.realizar_operacao_banco(
                    consulta=sql_erro,
                    parametros=dados_erro
                )
