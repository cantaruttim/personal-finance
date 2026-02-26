import pandas as pd

def ajuste_padrao_anomes(df, coluna: str):
    df[f'{coluna}'] = df[f'{coluna}'].astype(str).str.zfill(6)
    return df

def fillna_zero(df):
    df = df.fillna(0)
    return df

def gasto_total_mensal(df, value_discont, categorical, numerical):
    ''''
        Função que consolida por anomes a variação do gasto mensal.
    '''
    df['GASTO_MENSAL'] = (df.groupby(categorical)[numerical].transform('sum') - value_discont)
    return df

def gasto_total_consolidado(df):
    ''''
        Função que consolida por anomes a variação percentual do mês atual com o mês anterior.
    '''
    df = df[['ANOMES', 'GASTO_MENSAL']].drop_duplicates()
    df['PERC_VARIACAO'] = round((df['GASTO_MENSAL'] - df['GASTO_MENSAL'].shift(1)) / df['GASTO_MENSAL'], 6) * 100
    return df