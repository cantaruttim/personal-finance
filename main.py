import pandas as pd
from config.config import FILE_PATH

gastos = pd.read_excel(FILE_PATH, sheet_name='gastos')
print(gastos)