import pandas as pd
from config.config import FILE_PATH, FILE_PATH_OUTPUT
from util.util import (
    ajuste_padrao_anomes, 
    gasto_total_consolidado,
    gasto_total_mensal,
    fillna_zero,
    borrowed_money_by_anomes
)

gastos = pd.read_excel(FILE_PATH, sheet_name='gastos')
gastos = ajuste_padrao_anomes(gastos, 'ANOMES')
gastos = gasto_total_mensal(gastos, 2050, 'ANOMES', 'VALUE') ## value must be by month
df = fillna_zero(gasto_total_consolidado(gastos))

gastos = gastos.drop(columns=['GASTO_MENSAL'])
gastos = gastos.merge(df, on="ANOMES", how="left")

print(gastos)


df = gastos.groupby('ANOMES')['PERC_VARIACAO'].mean()
print(df)


notmy = borrowed_money_by_anomes(gastos)
# notmy = notmy[['ANOMES', 'BORROWED']]
# print(notmy)

# print("Salvando arquivo consolidado ... ")
# try:
#     gastos.to_excel(f"{FILE_PATH_OUTPUT}finance_report_consolidated.xlsx", index=False)
#     print("Documento salvo com sucesso!!!")
# except:
#     print(ValueError)
