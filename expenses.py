import pandas as pd
from config.config import FILE_PATH

SHEET_NAME = "card_expenses"

revenues = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME
)

print(revenues)