import requests
# from airflow.models import Variable
from datetime import datetime, timedelta
from typing import List
from src.servico.i_servico_api import IServicoAPI
# https://dadosabertos.almg.gov.br


class APILegislacao(IServicoAPI):
    def __init__(self):
        # self.__URL_BASE = Variable.get('api_dados_abertos_mg')
        self.__URL_BASE = 'https://dadosabertos.almg.gov.br'
        self.__data_final = datetime.now().strftime('%Y%m%d')
        self.__intervalo_dias = 60
        self.__data_inicial = (
            datetime.now() - timedelta(days=self.__intervalo_dias)).strftime('%Y%m%d')

    def obter_proposicoes(self) -> List:
        """Método para obter as proposicoes

        Returns:
            List: _description_
        """
        url = f'{self.__URL_BASE}/ws/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ord=3&p=1&ini={self.__data_inicial}&fim={self.__data_inicial}'
        req = requests.get(url=url)
        req = req.json()
        return req['resultado']['listaItem']


a = APILegislacao()
print(type(a.obter_proposicoes()))
