import pandas as pd
import re

substraction = [
    "D CLINIC ESTETICA", 
    "JIM.COM D CLINIC E", 
    "Wellhub Josias Santos F",
    "Wellhub Ivanir Dos Sant"
]

'''
 "===================="
 "===FUNÇÕES GERAIS==="
 "====================="
'''

def salva_multiplas_abas(abas_dict, file_path_output, file_name):
    """
    Salva múltiplos DataFrames em um único arquivo Excel, cada um em uma aba.
    
    Args:
        abas_dict: dicionário no formato {nome_da_aba: dataframe}
        file_path_output: caminho da pasta onde salvar
        file_name: nome do arquivo (sem extensão)
    """
    caminho_completo = f"{file_path_output}{file_name}.xlsx"
    print(f"Salvando arquivo com {len(abas_dict)} abas em {caminho_completo}...")
    
    try:
        with pd.ExcelWriter(caminho_completo, engine='openpyxl') as writer:
            for nome_aba, df in abas_dict.items():
                print(f"  -> Criando aba '{nome_aba}' com {len(df)} linhas")
                df.to_excel(writer, sheet_name=nome_aba, index=False)
        print(f"✅ Arquivo salvo com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")

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
        df.groupby(categorical)[numerical].transform('sum') + df[value_discont]
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
    '''
    Calcula o valor total emprestado com base na MACRO_CATEGORY
    '''
    emprestado = (
        df[df['MACRO_CATEGORY'] == 'EMPRÉSTIMOS']['VALUE']
        .sum()
    )
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
    pattern = '|'.join(substraction)

    notmy = df[df['DESCRIPTION'].str.contains(pattern, na=False)]
    notmy = notmy[['ANOMES', 'VALUE']]
    notmy['BORROWED'] = notmy['VALUE'] * -1
    notmy = notmy[['ANOMES', 'BORROWED']]

    return notmy

def group_macro_category(df):

    result = (
        df.groupby(['ANOMES', 'MACRO_CATEGORY'])['VALUE']
        .sum()
        .reset_index()
    )
    return result
