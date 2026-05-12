import pandas as pd
import numpy as np
from util.util import (
    ajuste_padrao_anomes
)

def retornando_ultima_fatura(df):
    from datetime import datetime
    ano = str(datetime.today().year)
    mes = str(datetime.today().month - 1)
    mes = '0' + mes
    anomes = str(mes + ano)
    
    return df[df['ANOMES'] == anomes]

install = pd.read_excel('./data/finance_report.xlsx' , 'parcelados')
install = ajuste_padrao_anomes(install, 'ANOMES')

install['STATUS'] = np.where(
    (install['PARC_ATUAL'] < install['ULTI_PARC']) |
    ((install['PARC_ATUAL'] == '-') & (install['ULTI_PARC'] == '-')),
    'Paying',
    'Over'
)

paying = install[ install['STATUS'] == "Paying" ]
over = install[ install['STATUS'] == "Over" ]

paying['TOTAL'] = paying.groupby('ANOMES')['VALUE'].transform('sum')
over['TOTAL'] = over.groupby('ANOMES')['VALUE'].transform('sum')

paying = retornando_ultima_fatura(paying)
over = retornando_ultima_fatura(over)

print("="*60)
print("OVER")
print("="*60)
print(over)

print("\n")
print("="*60)
print("PAYING")
print("="*60)
print(paying)
