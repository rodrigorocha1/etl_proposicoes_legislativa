from src.servico.api_legislacao import APILegislacao


api_legislacao = APILegislacao()


for dados, url in api_legislacao.obter_proposicoes():

    for tramitacao in dados['listaHistoricoTramitacoes']:
        print(url)
        print(tramitacao['data'].encode(
            'latin1').decode('utf-8').strip())
        print(tramitacao['historico'].encode(
            'latin1').decode('utf-8').strip())
        print(tramitacao['local'].encode(
            'latin1').decode('utf-8').strip())
        print()
