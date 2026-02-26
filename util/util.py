import pandas as pd

'''
 "===================="
 "===FUNÇÕES GERAIS==="
 "====================="
'''

def ajuste_padrao_anomes(df, coluna: str):
    ''''
        Ajusta o padrão do ANOMES para MMYYYY
    '''
    df[f'{coluna}'] = df[f'{coluna}'].astype(str).str.zfill(6)
    return df


def fillna_zero(df):
    '''Substitui os casos NaN -> 0'''
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

    
def select_columns(df, columns: list):
    """
    Seleciona uma lista de colunas de maneira dinâmica
    """
    return df[columns].drop_duplicates()

'''
 "============================="
 "===FUNÇÕES PARA PARCELADOS==="
 "============================="
'''

def filtrar_mes_mais_recente(df, coluna_anomes='ANOMES'):
    """
    Retorna apenas as linhas do mês mais recente com base na coluna ANOMES (formato MMYYYY).
    
    Parâmetros:
        df (pd.DataFrame): DataFrame original
        coluna_anomes (str): Nome da coluna que contém MMYYYY
    
    Retorna:
        pd.DataFrame: DataFrame filtrado apenas com o mês mais recente
    """
    
    # Converte temporariamente para datetime (sem criar coluna no df)
    datas = pd.to_datetime(
        df[coluna_anomes].astype(str),
        format='%m%Y',
        errors='coerce'
    )
    
    # Identifica a data mais recente
    data_max = datas.max()
    
    # Filtra apenas o mês mais recente
    df_filtrado = df[datas == data_max].copy()
    
    return df_filtrado
