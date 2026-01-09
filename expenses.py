import pandas as pd
from config.config import FILE_PATH
from utils import total_expend_on_month, cards_onwers

SHEET_NAME = "card_expenses"

expenses = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME
)

expenses = total_expend_on_month(
    expenses, 
    'yearmonth', 
    'value'
)

# print(expenses)