from dags.src.servico.api_legislacao import APILegislacao


api_legislacao = APILegislacao()


for dados in api_legislacao.obter_proposicoes():
    print(dados[1])
    print()
    print(dados[0])
