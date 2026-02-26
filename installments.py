import pandas as pd
from config.config import FILE_PATH_INSTALL
from util.util import (
    ajuste_padrao_anomes, 
    filtrar_mes_mais_recente
)

install = pd.read_excel(FILE_PATH_INSTALL , 'installments')
install = ajuste_padrao_anomes(install, 'ANOMES')


rec = filtrar_mes_mais_recente(install)
print(rec)
# print(install)