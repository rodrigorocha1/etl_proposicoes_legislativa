import requests

url = 'https://dadosabertos.almg.gov.br/ws/proposicoes/pesquisa/direcionada?formato=json&num=3147'

req = requests.get(url=url)
req.encoding = 'utf-8'
print(req.json())
