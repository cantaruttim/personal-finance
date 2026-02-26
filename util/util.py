import pandas as pd

value_discont = 2050

def ajuste_padrao_anomes(df, coluna: str):
    df[f'{coluna}'] = df[f'{coluna}'].astype(str).str.zfill(6)
    return df

def gasto_total_mensal(df, value_discont, categorical, numerical):
    df['GASTO_MENSAL'] = (df.groupby(categorical)[numerical].transform('sum') - value_discont)
    return df