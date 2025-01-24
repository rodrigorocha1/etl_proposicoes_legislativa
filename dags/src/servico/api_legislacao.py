import requests
# from airflow.models import Variable
from datetime import datetime, timedelta
from typing import Dict, Generator, List
from src.servico.i_servico_api import IServicoAPI
from time import sleep
# https://dadosabertos.almg.gov.br


class APILegislacao(IServicoAPI):
    def __init__(self):
        # self.__URL_BASE = Variable.get('api_dados_abertos_mg')
        self.__URL_BASE = 'https://dadosabertos.almg.gov.br'
        self.__data_final = datetime.now().strftime('%Y%m%d')
        self.__intervalo_dias = 60
        self.__data_inicial = (
            datetime.now() - timedelta(days=self.__intervalo_dias)).strftime('%Y%m%d')

    def obter_proposicoes(self) -> Generator[Dict, None, None]:
        """Método para Gerar de proposições

        Yields:
            Generator[Dict, None, None]: Gerador de dicionarios
        """
        url = f'{self.__URL_BASE}/ws/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ord=3&p=1&ini={self.__data_inicial}&fim={self.__data_final}'
        p = 1
        print(url)
        while True:
            try:
                sleep(3)
                req = requests.get(url=url)
                req.raise_for_status()
                dados = req.json()
                if dados['resultado']['noOcorrencias'] == 0:
                    break

                yield from dados['resultado']['listaItem']
                p += 1
                url = f'{self.__URL_BASE}/ws/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ord=3&p={p}&ini={self.__data_inicial}&fim={self.__data_final}'

            except requests.RequestException as e:
                print(f"Erro ao acessar a API: {e}")
                break
            except KeyError as e:
                print(f"Erro ao processar a resposta da API: {e}")
                break
