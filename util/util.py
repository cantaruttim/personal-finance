from datetime import datetime
from matplotlib.dates import relativedelta
import pandas as pd

substraction = [
    "D CLINIC ESTETICA", 
    "JIM.COM D CLINIC E", 
    "Wellhub Josias Santos F",
    "Wellhub Ivanir Dos Sant"
]

# ==================================================
# FUNÇÕES GERAIS
# ==================================================

def inverter_sinal_transacoes(df, patterns, column='DESCRIPTION', value_column='VALUE'):
    """
    Inverte o sinal do VALUE para transações cuja descrição contenha algum padrão da lista.
    """
    if patterns is None:
        return df
    pattern = '|'.join(patterns)
    mask = df[column].str.contains(pattern, na=False, case=False)
    df.loc[mask, value_column] = df.loc[mask, value_column] * -1
    return df

def salva_multiplas_abas(abas_dict, file_path_output, file_name):
    """
    Salva múltiplos DataFrames em um único arquivo Excel, cada um em uma aba.
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
    """
    Ajusta o padrão do ANOMES para MMYYYY (6 dígitos).
    """
    df[f'{coluna}'] = df[f'{coluna}'].astype(str).str.zfill(6)
    return df

def fillna_zero(df):
    """Substitui os casos NaN por 0."""
    df = df.fillna(0)
    return df

def gasto_total_mensal(df, value_discont, categorical, numerical):
    """
    Calcula GASTO_MENSAL (soma do numerical por categoria + value_discont).
    NOTA: Não aplica nenhum filtro de exclusão; a inversão de sinal deve ser feita antes.
    """
    if value_discont not in df.columns:
        raise ValueError(f'Coluna {value_discont} não encontrada no DataFrame')
    df[value_discont] = df[value_discont].fillna(0)
    df['GASTO_MENSAL'] = (
        df.groupby(categorical)[numerical].transform('sum') + df[value_discont]
    )
    return df

def gasto_total_consolidado(df):
    """
    Consolida por ANOMES a variação percentual do mês atual com o mês anterior.
    """
    df = df[['ANOMES', 'GASTO_MENSAL']].drop_duplicates()
    df['PERC_VARIACAO'] = round((df['GASTO_MENSAL'] - df['GASTO_MENSAL'].shift(1)) / df['GASTO_MENSAL'], 6) * 100
    return df

def select_columns(df, columns: list):
    """Seleciona uma lista de colunas de maneira dinâmica."""
    return df[columns].drop_duplicates()

# ========================
# FUNÇÕES PARA PARCELADOS
# ========================

def mes_para_datetime(anomes: str) -> datetime:
    """Converte 'MMYYYY' para datetime (primeiro dia do mês)."""
    try:
        mes = int(anomes[:2])
        ano = int(anomes[2:])
        return datetime(ano, mes, 1)
    except Exception as e:
        print(f"Erro ao converter {anomes}: {e}")
        return datetime(1900, 1, 1)

def calcular_termino(data_atual: datetime, meses_restantes: int) -> datetime:
    """Adiciona meses à data atual."""
    return data_atual + relativedelta(months=meses_restantes)


def filtrar_mes_mais_recente(df, coluna_anomes='ANOMES'):
    """
    Retorna apenas as linhas do mês mais recente com base na coluna ANOMES (formato MMYYYY).
    """
    datas = pd.to_datetime(df[coluna_anomes].astype(str), format='%m%Y', errors='coerce')
    data_max = datas.max()
    return df[datas == data_max].copy()

# def comprometimento_fatura_proximo_mes(df):
#     """
#     Calcula o valor da próxima fatura baseado no valor das parcelas já comprometidas.
#     """
#     mask = df['PAID'] <= df['TOTAL']
#     df['COMPROMETIDO'] = df['VALUE'].where(mask, 0).cumsum()
#     return df

def atualizar_comprometido_liquido(df, empr, coluna='COMPROMETIDO'):
    """
    Substitui a coluna COMPROMETIDO pelo valor final acumulado menos o valor emprestado.
    """
    df = df.copy()
    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")
    if df.empty:
        raise ValueError("O DataFrame está vazio.")
    valor_final = df[coluna].iloc[-1] - empr
    df[coluna] = valor_final
    return df

def borrowed_money_by_anomes(df, patterns=None):
    """
    Retorna o valor emprestado (negativo) das transações que casam com patterns.
    (Útil apenas para relatório, não usado no cálculo principal.)
    """
    if patterns is None:
        return pd.DataFrame(columns=['ANOMES', 'BORROWED'])
    pattern = '|'.join(patterns)
    borrowed = df[df['DESCRIPTION'].str.contains(pattern, na=False, case=False)].copy()
    if borrowed.empty:
        return pd.DataFrame(columns=['ANOMES', 'BORROWED'])
    borrowed['BORROWED'] = borrowed['VALUE'] * -1
    return borrowed[['ANOMES', 'BORROWED']]

def group_categories(df, col_main, col_sub=None, value_name='VALUE'):
    """
    Agrupa gastos por ANOMES e categoria(s).
    NOTA: Não aplica nenhum filtro de exclusão; a inversão de sinal deve ser feita antes.
    """
    if col_sub:
        result = (
            df.groupby(['ANOMES', col_main, col_sub])['VALUE']
              .sum()
              .reset_index()
        )
    else:
        result = (
            df.groupby(['ANOMES', col_main])['VALUE']
              .sum()
              .reset_index()
        )
    result = result.rename(columns={'VALUE': value_name})
    return result
