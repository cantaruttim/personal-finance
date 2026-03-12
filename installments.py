import pandas as pd
import numpy as np
from util.util import (
    ajuste_padrao_anomes,
    gasto_total_mensal
)

install = pd.read_excel('./data/finance_report.xlsx' , 'parcelados')
install = ajuste_padrao_anomes(install, 'ANOMES')

install['STATUS'] = np.where(
    (install['PARC_ATUAL'] < install['ULTI_PARC']) |
    ((install['PARC_ATUAL'] == '-') & (install['ULTI_PARC'] == '-')),
    'Paying',
    'Over'
)

paying = install[ install['STATUS'] == "Paying"]
over = install[ install['STATUS'] == "Over"]

paying['TOTAL'] = paying.groupby('ANOMES')['VALUE'].transform('sum')
over['TOTAL'] = over.groupby('ANOMES')['VALUE'].transform('sum')

print(over)
print(paying)