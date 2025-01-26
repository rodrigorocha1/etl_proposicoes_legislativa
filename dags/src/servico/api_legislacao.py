import requests
# from airflow.models import Variable
from datetime import datetime, timedelta
from typing import Dict, Generator, List, Tuple
from src.servico.i_servico_api import IServicoAPI
from time import sleep
# https://dadosabertos.almg.gov.br


class APILegislacao(IServicoAPI):
    def __init__(self):
        # self.__URL_BASE = Variable.get('api_dados_abertos_mg')
        self.__URL_BASE = 'https://dadosabertos.almg.gov.br'
        self.__data_final = datetime.now().strftime('%Y%m%d')
        self.__intervalo_dias = 3
        self.__data_inicial = (
            datetime.now() - timedelta(days=self.__intervalo_dias)).strftime('%Y%m%d')

    def obter_proposicoes(self) -> Generator[Tuple[Dict, str], None, None]:
        """_summary_

        Yields:
            Generator[tuple[Dict, str], None, None]: _description_
        """

        url = f'{self.__URL_BASE}/ws/proposicoes/pesquisa/direcionada'
        p = 1

        while True:
            try:
                sleep(3)
                req = requests.get(url=url, params={
                    'tp': '1000',
                    'formato': 'json',
                    'ano': '2024',
                    'ord': '3',
                    'p': p,
                    'ini': self.__data_inicial,
                    'fim': self.__data_final
                })
                req.raise_for_status()

                req.encoding = 'latin-1'
                dados = req.json()
                if dados['resultado']['noOcorrencias'] == 0:
                    break

                for item in dados['resultado']['listaItem']:
                    yield item, req.url
                p += 1
                if p == 4:
                    break

            except requests.RequestException as e:
                print(f"Erro ao acessar a API: {e}")
                break
            except KeyError as e:
                print(f"Erro ao processar a resposta da API: {e}")
                break
