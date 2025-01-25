texto_com_erro = 'Deputada Ione Pinheiro UNI\xc3\x83O Deputada Beatriz Cerqueira PT Deputado Betinho Pinto Coelho PV Deputado'

# Corrigir a codificação
texto_corrigido = texto_com_erro.encode('latin1').decode('utf-8')

print(texto_corrigido)
