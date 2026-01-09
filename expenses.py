import pandas as pd
from config.config import FILE_PATH
from data.data import DANI_VALUE
from utils import total_expend_on_month, net_expend_excluding_borrowed

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

expenses2 = net_expend_excluding_borrowed(expenses)

print(expenses2)
print(expenses)