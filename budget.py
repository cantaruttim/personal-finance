import pandas as pd
from util.util import ajuste_padrao_anomes, filtrar_mes_mais_recente

## Cria a lógica do orçamento para cada categoria
budget = pd.read_excel('./data/relatorio_financeiro_completo.xlsx', sheet_name='sumarizacao_categorias')
holerite = pd.read_excel('./data/relatorio_holerites.xlsx', sheet_name='Pivot_mensal')

budget = ajuste_padrao_anomes(budget, 'ANOMES')
budget = filtrar_mes_mais_recente(budget, coluna_anomes='ANOMES')

budget = budget[    budget['VALUE_MACRO_CATEGORY'] > 0  ]

budget = (
    budget
        .sort_values('categoria_macro', ascending=True)
        .sort_values('VALUE_MACRO_CATEGORY', ascending=True)
        .reset_index(drop=True)
)

print(budget)

print(holerite)