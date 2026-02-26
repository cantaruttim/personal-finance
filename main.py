import pandas as pd
from config.config import FILE_PATH
from util.util import ajuste_padrao_anomes, gasto_total_mensal

gastos = pd.read_excel(FILE_PATH, sheet_name='gastos')
gastos = ajuste_padrao_anomes(gastos, 'ANOMES')
gastos = gasto_total_mensal(gastos, 2050, 'ANOMES', 'VALUE')

print(gastos)
