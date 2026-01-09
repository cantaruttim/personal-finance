import pandas as pd

def normalize_yearmonth(df):
    df = df.copy()
    df['yearmonth'] = df['yearmonth'].astype(str).str.zfill(6)
    return df

def parse_ptbr_money(series):
    s = series.astype(str)

    has_comma = s.str.contains(',')

    s.loc[has_comma] = (
        s.loc[has_comma]
        .str.replace('.', '', regex=False)  
        .str.replace(',', '.', regex=False) 
    )

    return s.astype(float)


def total_expend_on_month(
        df,
        categorical: list,
        numerical: float,
    ):

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
