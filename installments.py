import pandas as pd
import numpy as np
from util.util import (
    ajuste_padrao_anomes,
    filtrar_mes_mais_recente,
    inverter_sinal_transacoes,
    substraction
)

install = pd.read_excel('./data/finance_report.xlsx' , 'parcelados')
install = ajuste_padrao_anomes(install, 'ANOMES')
install = filtrar_mes_mais_recente(install, coluna_anomes='ANOMES')
install = inverter_sinal_transacoes(install, substraction)
install['PARC_ATUAL'] = install['PARC_ATUAL'].astype(int)
install['ULTI_PARC'] = install['ULTI_PARC'].astype(int)
install['VALUE'] = install['VALUE'].astype(float)

install['STATUS'] = np.where(
    (install['PARC_ATUAL'] < install['ULTI_PARC']) |
    ((install['PARC_ATUAL'] == '-') & (install['ULTI_PARC'] == '-')),
    'Paying',
    'Over'
)

paying = install[ install['STATUS'] == "Paying" ]
over = install[ install['STATUS'] == "Over" ]

paying = filtrar_mes_mais_recente(paying, coluna_anomes='ANOMES')
over = filtrar_mes_mais_recente(over, coluna_anomes='ANOMES')

resumo_mes = pd.DataFrame({
    'ANOMES': [paying['ANOMES'].iloc[0]],
    'TOTAL_PAYING': [paying[paying['VALUE'] > 0]['VALUE'].sum()],
    'TOTAL_OVER': [over[over['VALUE'] > 0]['VALUE'].sum()],
    'TOTAL_GERAL': [paying[paying['VALUE'] > 0]['VALUE'].sum() + over[over['VALUE'] > 0]['VALUE'].sum()]
})

print("="*60)
print("OVER")
print("="*60)
print(over)

print("\n")
print("="*60)
print("PAYING")
print("="*60)
print(paying)


print("\n")
print("="*60)
print("RESUMO MENSAL")
print("="*60)
print(resumo_mes)