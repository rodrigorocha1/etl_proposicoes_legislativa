dado = {
    'AUTOR': 'a',
    'DATA_PRESENTACAO': 'a',
    'EMENTA': 'assunto',
    'REGIME': 'proposicao',
    'SITUACCAO': 'proposicao',
    'TIPO_PROPOSICAO': 'proposicao',
    'NUMERO': 'proposicao',
    'ANO': 'proposicao',
    'CIDADE': 'Belo Horizonte',
    'ESTADO': 'Minas Gerais'
}


colunas = ", ".join(dado.keys())
print(colunas)
placeholders = ", ".join(
    [f"%({coluna})s" for coluna in dado.values()]
)
tabela = "proposicao"
sql_insersao = f"""
                INSERT INTO {tabela} ({colunas})
               VALUES ({placeholders})
 """

print(sql_insersao)
