import pandas as pd
from util.grafic_viz import grafico_um

df = pd.read_excel('./data/finance_report_consolidated.xlsx')

print("-----------------")
grafico_um(df)
