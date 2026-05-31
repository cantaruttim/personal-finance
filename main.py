import pandas as pd
import re
from config.config import FILE_PATH, FILE_PATH_OUTPUT
from util.util import (
    ajuste_padrao_anomes,
    gasto_total_consolidado,
    gasto_total_mensal,
    fillna_zero, 
    borrowed_money_by_anomes,
    group_categories,
    salva_multiplas_abas,
    inverter_sinal_transacoes,
    substraction
)

gastos = pd.read_excel(FILE_PATH, sheet_name='gastos')
gastos = ajuste_padrao_anomes(gastos, 'ANOMES')
gastos = inverter_sinal_transacoes(gastos, substraction)

print('\n')
print("conferindo valor total mensal ... ")
print(gastos.groupby('ANOMES')['VALUE'].sum())
print('\n')

notmy = borrowed_money_by_anomes(gastos)  
notmy = notmy[['ANOMES', 'BORROWED']]
borrowed_grouped = notmy.groupby('ANOMES', as_index=False)['BORROWED'].sum()

print('\n')
gastos = gastos.merge(borrowed_grouped, on='ANOMES', how='left')
print('\n')

gastos = gasto_total_mensal(gastos, 'BORROWED', 'ANOMES', 'VALUE')
print("\n")
print("Realizando tratamentos iniciais ...")
df = fillna_zero(gasto_total_consolidado(gastos))

gastos = gastos.drop(columns=['GASTO_MENSAL'])
gastos = gastos.merge(df, on="ANOMES", how="left")

print("\n")
print("Seu relatório está quase pronto ...")
print(gastos)
print("\n")

def clean_dataframe(df):
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df

gastos = clean_dataframe(gastos)

macro_category = group_categories(gastos, 'CD_CATEGORY')
sub_category = group_categories(gastos, 'CD_CATEGORY', 'CD_SUB_CATEGORY')

print(macro_category)
print("\n")
print(sub_category)
print("\n")

# Renomeia colunas
macro_category = macro_category.rename(columns={'VALUE': 'VALUE_MACRO_CATEGORY'})
sub_category = sub_category.rename(columns={'VALUE': 'VALUE_SUB_CATEGORY'})

# Mescla com o DataFrame original
gastos = gastos.merge(macro_category, on=["ANOMES", "CD_CATEGORY"], how="left")
gastos = gastos.merge(sub_category, on=["ANOMES", "CD_CATEGORY", "CD_SUB_CATEGORY"], how="left")

print("\nTABELA CONSOLIDADA:")
print(gastos)
print("\n")

# ========== ANÁLISE DAS CATEGORIAS ==========
print("="*60)
print("CATEGORIAS")
print("="*60)

categorias = gastos[['ANOMES', 'CD_CATEGORY', 'CD_SUB_CATEGORY', 'VALUE_MACRO_CATEGORY', 'VALUE_SUB_CATEGORY']].drop_duplicates()
print(categorias)
print("\n")

# ========== SALVANDO O ARQUIVO ==========
print("="*60)
print("SALVANDO O ARQUIVO CONSOLIDADO")
print("="*60)

abas = {
    "consolidado_por_mes": df,
    "detalhamento_gastos": gastos,
    "resumo_emprestimos": borrowed_grouped,
    "sumarizacao_categorias": categorias
}

try:
    salva_multiplas_abas(abas, FILE_PATH_OUTPUT, "relatorio_financeiro_completo")
    print("✅ Arquivo salvo com sucesso!")
except Exception as e:
    print(f"❌ Error: {e}")