import pandas as pd
from config.config import (
    FILE_PATH, 
    FILE_PATH_OUTPUT, 
    FILE_NAME
)
from util.util import (
    ajuste_padrao_anomes, 
    gasto_total_consolidado,
    gasto_total_mensal,
    fillna_zero,
    borrowed_money_by_anomes,
    salva_arquivo_consolidado,
    add_macro_category_fast,
    group_macro_category,
    clean_columns
)


gastos = pd.read_excel(FILE_PATH, sheet_name='gastos')
gastos = ajuste_padrao_anomes(gastos, 'ANOMES')

print('\n')
print("conferindo valor total mensal ... ")
print(gastos.groupby('ANOMES')['VALUE'].sum())
print('\n')

notmy = borrowed_money_by_anomes(gastos)
notmy = notmy[['ANOMES', 'BORROWED']]
borrowed_grouped = (
    notmy.groupby('ANOMES', as_index=False)['BORROWED'].sum()
)

print('\n')
gastos = gastos.merge(
    borrowed_grouped,
    on='ANOMES',
    how='left'
)

print('\n')

gastos = (
    gasto_total_mensal(
        gastos, 
        'BORROWED', 
        'ANOMES', 
        'VALUE'
    )
)
print("\n")
print("Realizando tratamentos iniciais ...")
df = fillna_zero(gasto_total_consolidado(gastos))

gastos = gastos.drop(columns=['GASTO_MENSAL'])
gastos = gastos.merge(df, on="ANOMES", how="left")

gastos = add_macro_category_fast(gastos)

categories = group_macro_category(gastos)


gastos = gastos.merge(
    categories,
    on=['ANOMES', 'MACRO_CATEGORY'],
    how='left',
    suffixes=('', '_BY_MACRO_CATEGORY')
)

gastos = clean_columns(gastos)

print("\n")
print("Seu relatório está quase pronto ...")
print(gastos)
print("\n")

salva_arquivo_consolidado(df, FILE_PATH_OUTPUT, FILE_NAME)
salva_arquivo_consolidado(gastos, FILE_PATH_OUTPUT, "finance_personal_report.xlsx")