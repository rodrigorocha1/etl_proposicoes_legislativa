from src.servico.api_legislacao import APILegislacao
from src.servico.opercacoes_banco import OperacaoBanco


class ETL:
    def __init__(self):
        self.__api_legislacao = APILegislacao()
