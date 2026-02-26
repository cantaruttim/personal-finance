import pandas as pd
from config.config import FILE_PATH_INSTALL
from util.util import (
    ajuste_padrao_anomes, 
    filtrar_mes_mais_recente,
    comprometimento_fatura_proximo_mes,
    retorna_valor_emprestado,
    atualizar_comprometido_liquido
)

install = pd.read_excel(FILE_PATH_INSTALL , 'installments')
install = ajuste_padrao_anomes(install, 'ANOMES')
install = filtrar_mes_mais_recente(install)
install = comprometimento_fatura_proximo_mes(install)
empr = retorna_valor_emprestado(install)
install = atualizar_comprometido_liquido(install, empr)

print(install)
