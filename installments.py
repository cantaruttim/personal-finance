# imports
import pandas as pd
from config.config import FILE_PATH
from data.data import DANI_VALUE
from utils import (
    parse_ptbr_money,
    total_expend_on_month, 
    cards_owners, 
    select_columns,
    normalize_yearmonth
)

# global variables
SHEET_NAME = "installments"
card_expenses = cards_owners(FILE_PATH, "card_expenses")

# sheet used in 
def read_installment():
    installment = pd.read_excel(
        FILE_PATH,
        sheet_name=SHEET_NAME
    )
    return installment

installment = read_installment()

def build_installments_report(installment):
    # initial treatments
    installment['value'] = parse_ptbr_money(installment['value'])
    installment = normalize_yearmonth(installment)
    installment = total_expend_on_month(installment, 'yearmonth', 'value')

    # merging information
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

    installment['total_expend_on_month'] = installment['total_expend_on_month'] - DANI_VALUE
    return installment
