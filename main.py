import pandas as pd
from config.config import FILE_PATH
from util.util import (
    ajuste_padrao_anomes, 
    gasto_total_mensal, 
    gasto_total_consolidado,
    fillna_zero
)

gastos = pd.read_excel(FILE_PATH, sheet_name='gastos')
gastos = ajuste_padrao_anomes(gastos, 'ANOMES')
gastos = gasto_total_mensal(gastos, 2050, 'ANOMES', 'VALUE')

df = fillna_zero(gasto_total_consolidado(gastos))



print(df)
