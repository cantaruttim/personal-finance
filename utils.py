import pandas as pd

def normalize_yearmonth(df):
    df = df.copy()
    df['yearmonth'] = df['yearmonth'].astype(str).str.zfill(6)
    return df

def parse_ptbr_money(series: pd.Series, force_ptbr=False) -> pd.Series:
    s = series.copy()

    if force_ptbr:
        s = (
            s.astype(str)
            .str.strip()
            .str.replace('R$', '', regex=False)
            .str.replace(' ', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )
        return pd.to_numeric(s, errors='coerce')

    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)

    return (
        s.astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

def total_expend_on_month(
        df: pd.DataFrame,
        categorical,
        numerical
    ):

    df = df.copy()
    df['total_expend_on_month'] = (
        df
        .groupby(categorical)[numerical]
        .transform('sum')
    )
    return df

def cards_onwers(FILE_PATH, SHEET_NAME):
    df = pd.read_excel( FILE_PATH, SHEET_NAME)
    return (
        df[['card', 'owner']]
        .drop_duplicates()
        .reset_index(drop=True)
    )

def select_columns(df, columns):
    return df[columns]
