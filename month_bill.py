import pandas as pd
from utils import (
    total_expend_on_month,
    select_columns
)
from data.data import DANI_VALUE
from config.config import (
    FILE_PATH
)

SHEET_NAME = "fixed_consumption"
df = pd.read_excel(FILE_PATH, SHEET_NAME)

def consolidated_expenses():
    df = total_expend_on_month(df, 'yearmonth', 'value')
    df = select_columns(df, ['yearmonth','total_expend_on_month'])
    df['real_expenses'] = df['total_expend_on_month'] - DANI_VALUE

    df = df.sort_values('yearmonth', ascending=True)
    df = df.groupby('yearmonth')[['total_expend_on_month','real_expenses']].mean()

    return df