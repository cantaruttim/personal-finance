import pandas as pd
from config.config import FILE_PATH

SHEET_NAME = "installments"

installment = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME
)

# print(installment.info())

def total_expend_on_month(df):
    df['total_expend_on_month'] = (
        df
            .groupby('yearmonth', as_index=False)['value']
            .transform('sum')
        )
    return df
installment = total_expend_on_month(installment)

print(installment)