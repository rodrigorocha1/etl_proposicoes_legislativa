import pytz
from datetime import datetime

# Definindo o fuso horário de Brasília
brasilia_tz = pytz.timezone('America/Sao_Paulo')

# Ajustando o start_date para o horário de Brasília
start_date_brasilia = datetime.now()
start_date_brasilia = brasilia_tz.localize(start_date_brasilia)

print(start_date_brasilia.strftime('%Y-%m-%d %H:%M:%S'))
