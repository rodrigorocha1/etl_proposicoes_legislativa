from datetime import datetime
import pytz


def obter_data_registro() -> str:
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    data_registro = datetime.now()
    data_registro = data_registro.astimezone(
        brasilia_tz).strftime('%Y-%m-%d %H:%M:%S')
    print(type(data_registro))
    return data_registro


dados = obter_data_registro()
print(dados)
