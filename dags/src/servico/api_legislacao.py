import requests
# from airflow.models import Variable
from datetime import datetime, timedelta
from typing import Dict, Generator, Optional, Tuple
from src.servico.i_servico_api import IServicoAPI
from time import sleep
# https://dadosabertos.almg.gov.br


class APILegislacao(IServicoAPI):
    def __init__(self):
        # self.__URL_BASE = Variable.get('api_dados_abertos_mg')
        self.__URL_BASE = 'https://dadosabertos.almg.gov.br'
        self.__data_final = datetime.now().strftime('%Y%m%d')
        self.__intervalo_dias = 10
        self.__data_inicial = (
            datetime.now() - timedelta(days=self.__intervalo_dias)).strftime('%Y%m%d')

    def obter_proposicoes(self, numero: Optional[str] = None) -> Generator[Tuple[Dict, str], None, None]:
        """_summary_

        Yields:
            Generator[tuple[Dict, str], None, None]: _description_
        """

        url = f'{self.__URL_BASE}/ws/proposicoes/pesquisa/direcionada'
        p = 1

        while True:
            try:
                sleep(3)
                if numero is None:
                    params = {
                        'tp': '1000',
                        'formato': 'json',
                        'ano': '2024',
                        'ord': '3',
                        'p': p,
                        'ini': self.__data_inicial,
                        'fim': self.__data_final
                    }
                    flag = True

                else:
                    params = {
                        'formato': 'json',
                        'ano': '2024',
                        'numero': numero
                    }
                    flag = False
                req = requests.get(url=url, params=params)

                req.raise_for_status()

                req.encoding = 'latin-1'
                dados = req.json()
                print(dados, req.url)
                if dados['resultado']['noOcorrencias'] == 0:
                    break

                for item in dados['resultado']['listaItem']:
                    yield item, req.url

                if not flag:
                    break
                p += 1
                if p == 4:
                    break

            except requests.RequestException as e:
                print(f"Erro ao acessar a API: {e}")
                break
            except KeyError as e:
                print(f"Erro ao processar a resposta da API: {e}")
                break
