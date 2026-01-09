import pandas as pd

def total_expend_on_month(
        df, 
        categorical: list, 
        numerical: float,
        operation
    ):
    df['total_expend_on_month'] = (
        df
            .groupby(categorical, as_index=False)[numerical]
            .transform(operation)
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
