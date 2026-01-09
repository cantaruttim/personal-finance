import pandas as pd
from config.config import FILE_PATH
from utils import total_expend_on_month, cards_onwers, select_columns

SHEET_NAME = "installments"

card_expenses = cards_onwers(FILE_PATH, "card_expenses")

installment = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME
)

installment = total_expend_on_month(
    installment, 
    'yearmonth', 
    'value',
    'sum'
) 


installment = installment.merge(
    card_expenses, 
    on='card', 
    how='left',
    suffixes=('', '_from_cards')
)

installment = select_columns(
    installment, 
    ['card','card_flag','yearmonth','value','actual_installment','final_installment','total_expend_on_month','owner_from_cards']
)

print(installment)
