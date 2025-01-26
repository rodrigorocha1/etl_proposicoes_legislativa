dados = {
    "resultado": {
        "banco": "MATE",
        "consulta": "(11050)[NUME]  E  (2024)[ANO]",
        "noOcorrencias": 2,
        "noDocumentos": 1,
        "tamanhoPagina": 20,
        "numPagina": 1,
        "ordenacao": "tipo,-@ano,-@nume",
        "dataHora": {
            "date": "2025-01-26"
        },
        "erro": 'fflse',
        "listaItem": [
            {
                "dominio": "Remissivo",
                "tipoProjeto": "REQUERIMENTO DE COMISSÃO",
                "siglaTipoProjeto": "RQC",
                "numero": "11050",
                "ano": "2024",
                "autor": "Deputado Professor Cleiton                 PV",
                "assunto": "Requer seja encaminhado ao Ministério Público de Minas Gerais – MPMG –\npedido de providências para proibir a entrada de torcedores da Mancha\nAlviverde no Estado, em especial em dias de jogos nas proximidades dos\neventos, tendo em vista o crime ocorrido em 26/10/2024, quando essa\ntorcida atacou a Máfia Azul, deixando um torcedor morto e 17 feridos.",
                "indexacao": "/Tema/Esporte e Lazer/Esporte/Modalidade Esportiva/Futebol\n/Tema/Segurança Pública/Crime/Crime Contra a Pessoa",
                "situacao": "Aprovado",
                "siglaSituacao": "APRVD",
                "situacaoGeral": "Proposições aprovadas",
                "siglaSituacaoGeral": "MAPRV",
                "dataPublicacao": "2025-01-23",
                "numeroDoc": "000000002",
                "proposicao": "RQC 11050 2024 - REQUERIMENTO DE COMISSÃO",
                "matricula": "26119",
                "regime": "Votado nas comissões",
                "local": "Comissão de Segurança Pública",
                "linkLegislacao": {},
                "atualizacao": "20250123",
                "horario": "0724",
                "dataUltimaAcao": "2024-10-30",
                "listaHistoricoTramitacoes": [
                    {
                        "passo": 1,
                        "data": "2024-10-30",
                        "local": "Comissão de Segurança Pública",
                        "historico": "Proposição recebida na Comissão.\nPublicado no DL em 23 1 2025, pág 1.\nAprovado o requerimento.\nDecisão publicada no DL em 23 1 2025, pág 1."
                    }
                ],
                "links": [
                    {
                        "expressao": "(RQN adj 8788 adj 2024[PROP])[dbmt]",
                        "banco": "mate",
                        "descricao": "RQN 8788 2024",
                        "url": "/proposicoes/pesquisa/avancada?expr=%28RQN+adj+8788+adj+2024%5BPROP%5D%29%5Bdbmt%5D",
                        "tipo": "RQN",
                        "numero": 8788,
                        "ano": 2024
                    }
                ],
                "linksProposicoesAnexadas": [],
                "acompanhamento": "N",
                "autoresEstruturados": [
                    {
                        "id": 26119,
                        "nome": "Deputado Professor Cleiton",
                        "partido": "PV"
                    }
                ]
            }
        ]
    }
}

a = dados['resultado']['listaItem']
print(a)
print()
a.append({'a': 1})

# Verificando o resultado
print(a)
