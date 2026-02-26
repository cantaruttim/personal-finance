import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline
from util.util import select_columns, ajuste_padrao_anomes

df = pd.read_excel('./data/finance_report_consolidated.xlsx')

print("Gráfico 1: \n")

df1 = select_columns(df, ['ANOMES', 'GASTO_MENSAL', 'PERC_VARIACAO'])

df1 = (
    df1[['ANOMES', 'GASTO_MENSAL', 'PERC_VARIACAO']]
    .groupby('ANOMES', as_index=False)
    .first()
)

df1['ANOMES'] = df1['ANOMES'].astype(str)
df1['DATA'] = pd.to_datetime(df1['ANOMES'], format='%m%Y')
df1 = df1.sort_values('DATA')
df1['LABEL'] = df1['DATA'].dt.strftime('%b/%Y')

x = df1['LABEL']
y = df1['GASTO_MENSAL']
y_linha = df1['PERC_VARIACAO']

fig, ax1 = plt.subplots(figsize=(10, 5))

bars = ax1.bar(x, y)
ax1.set_ylabel('Gasto Mensal')
ax1.set_xlabel('Ano/Mês')

for bar in bars:
    height = bar.get_height()

    if height > max(y) * 0.1:
        cor = 'white'
        deslocamento = -5
        alinhamento = 'top'
    else:
        cor = 'black'
        deslocamento = 5
        alinhamento = 'bottom'

    ax1.annotate(
        f'R$ {height:,.2f}',
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, deslocamento),
        textcoords="offset points",
        ha='center',
        va=alinhamento,
        color=cor,
        fontweight='bold'
    )
x_numeric = np.arange(len(x))
ax2 = ax1.twinx()

ax2.plot(x, y_linha, color='red', linewidth=.75)
ax2.set_ylabel('Variação (%)')

if len(x_numeric) > 2:
    x_smooth = np.linspace(x_numeric.min(), x_numeric.max(), 300)
    spline = make_interp_spline(x_numeric, y_linha, k=2)
    y_smooth = spline(x_smooth)

    ax2.plot(x_smooth, y_smooth, linewidth=2, color='red')
    ax2.set_xticks(x_numeric)
    ax2.set_xticklabels(x)
else:
    # Se só tiver 2 pontos, faz linha normal
    ax2.plot(x, y_linha, marker='o', color='red', linewidth=2)

plt.title('Gasto Mensal e Percentual de Variação')

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()