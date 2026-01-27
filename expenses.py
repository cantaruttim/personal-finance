# imports
import pandas as pd
from config.config import FILE_PATH
from data.data import DANI_VALUE
from utils import (
    parse_ptbr_money,
    total_expend_on_month, 
    normalize_yearmonth,
    perc_month_variation,
    fill_nan_with_zero,
    select_columns
)

# sheet used in
def read_expenses():
    expenses = pd.read_excel(
        FILE_PATH,
        sheet_name=SHEET_NAME
    )
    return expenses


# global variables
SHEET_NAME = "card_expenses"
df = total_expend_on_month(read_expenses(), "yearmonth", "value")

# initial treatments
def build_expenses_report(expenses):
    expenses['value'] = parse_ptbr_money(expenses['value'])
    expenses = normalize_yearmonth(expenses)
    expenses = total_expend_on_month(expenses, 'yearmonth', 'value')

    expenses['total_expend_on_month'] = expenses['total_expend_on_month'] - DANI_VALUE

    return expenses


def sum_expenses_dataframe(df):
    value = normalize_yearmonth(
        df
        .groupby('yearmonth', as_index=False)['value']
        .sum()
    )
    return value

def month_expenses_variation():
    perc_var = sum_expenses_dataframe(df)
    perc_var = select_columns(
        fill_nan_with_zero(
            perc_month_variation(perc_var)
        ), 
        ["yearmonth", "year", "month", "variation_percent"]
    )
    return perc_var