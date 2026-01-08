import pandas as pd

FILE_PATH = "./data/finance_report.xlsx"
SHEET_NAME = "installments"

installment = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME
)

print(installment)