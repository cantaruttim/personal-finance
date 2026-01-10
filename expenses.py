# imports
import pandas as pd
from config.config import FILE_PATH
from data.data import DANI_VALUE
from utils import (
    parse_ptbr_money,
    total_expend_on_month, 
    normalize_yearmonth
)

# global variables
SHEET_NAME = "card_expenses"

# sheet used in
expenses = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME
)

# initial treatments
def build_expenses_report():
    expenses['value'] = parse_ptbr_money(expenses['value'])
    expenses = normalize_yearmonth(expenses)
    expenses = total_expend_on_month(expenses, 'yearmonth', 'value')

    expenses['total_expend_on_month'] = expenses['total_expend_on_month'] - DANI_VALUE

    return expenses

expenses = build_expenses_report()
print(expenses)