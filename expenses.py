import pandas as pd
from config.config import FILE_PATH
from data.data import DANI_VALUE
from utils import (
    parse_ptbr_money,
    total_expend_on_month, 
    normalize_yearmonth
)

SHEET_NAME = "card_expenses"

expenses = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME
)

expenses['value'] = parse_ptbr_money(expenses['value'])
expenses = normalize_yearmonth(expenses)
expenses = total_expend_on_month(expenses, 'yearmonth', 'value')

print(expenses)