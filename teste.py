from src.etl import ETL
from src.servico.opercacoes_banco import OperacaoBanco
from src.servico.api_legislacao import APILegislacao


etl = ETL(api_legislacao=APILegislacao(), operacoes_banco=OperacaoBanco())

etl.realizar_etl_propicao()
