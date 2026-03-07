import pandas as pd

substraction = "D CLINIC ESTETICA"

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

    if value_discont not in df.columns:
        raise ValueError(f'Coluna {value_discont} não encontrada no DataFrame')

    df[value_discont] = df[value_discont].fillna(0)

    df['GASTO_MENSAL'] = (
        df.groupby(categorical)[numerical].transform('sum') +  df[value_discont]
    )
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
    
    datas = pd.to_datetime(
        df[coluna_anomes].astype(str),
        format='%m%Y',
        errors='coerce'
    )
    
    data_max = datas.max()
    
    df_filtrado = df[datas == data_max].copy()
    
    return df_filtrado


def comprometimento_fatura_proximo_mes(df):
    ''''
        Calcula o valor da próxima fatura baseado no valor das parcelas
        já comprometidas
    '''
    mask = df['PAID'] <= df['TOTAL']

    df['COMPROMETIDO'] = (
        df['VALUE']
        .where(mask, 0)
        .cumsum()
    )
    # valor = df['COMPROMETIDO'].iloc[-1:]
    return df

def retorna_valor_emprestado(df):
    ''''
        Calcula o valor total emprestado
        Valor deve ser abatido do valor total da fatura
    '''
    emprestado = (
        df[ df['DESCRIPTION'].str.contains("D CLINIC ESTETICA")]
    )
    emprestado = emprestado['VALUE'].sum()
    return emprestado


def atualizar_comprometido_liquido(df, empr, coluna='COMPROMETIDO'):
    """
    Substitui a coluna COMPROMETIDO pelo valor final acumulado
    menos o valor emprestado (empr).
    
    Parâmetros:
        df (pd.DataFrame): DataFrame original
        empr (float): valor a ser descontado
        coluna (str): nome da coluna acumulada
        
    Retorna:
        pd.DataFrame: DataFrame atualizado
    """
    
    df = df.copy()
    
    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")
    
    if df.empty:
        raise ValueError("O DataFrame está vazio.")
    
    valor_final = df[coluna].iloc[-1] - empr
    df[coluna] = valor_final
    
    return df


def borrowed_money_by_anomes(df):
    # not my
    notmy = df[ df['DESCRIPTION'].str.contains(substraction) ]
    notmy = notmy[['ANOMES', 'VALUE']]
    notmy['BORROWED'] = notmy['VALUE'] * -1
    notmy = notmy[['ANOMES', 'BORROWED']]
    # notmy = notmy.groupby('ANOMES')['VALUE'].sum()
    return notmy