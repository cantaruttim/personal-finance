import pandas as pd
import numpy as np
import pandas as pd    
from matplotlib.dates import relativedelta
from util.util import (
    mes_para_datetime,
    calcular_termino,
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


paying_commitment = paying.copy()

if 'paying_commitment' not in globals():
    raise NameError("O DataFrame 'paying_commitment' não foi encontrado. Certifique-se de que ele foi carregado antes.")

paying_commitment = paying.copy()  
paying_commitment = paying_commitment[paying_commitment['VALUE'] > 0]

# Valida se as colunas existem
colunas_obrigatorias = ['ANOMES', 'PARC_ATUAL', 'ULTI_PARC', 'VALUE']
for col in colunas_obrigatorias:
    if col not in paying_commitment.columns:
        raise ValueError(f"Coluna '{col}' não encontrada no DataFrame. Verifique os nomes.")

# Cria as projeções de gastos futuros
paying_commitment['PARC_REST'] = paying_commitment['ULTI_PARC'] - paying_commitment['PARC_ATUAL']
paying_commitment['GASTO_FUTURO'] = paying_commitment['VALUE'] * paying_commitment['PARC_REST']
paying_commitment['DATA_ATUAL'] = paying_commitment['ANOMES'].apply(mes_para_datetime)
paying_commitment['MES_TERMINO'] = paying_commitment.apply(lambda row: calcular_termino(row['DATA_ATUAL'], row['PARC_REST']), axis=1)
paying_commitment['MES_TERMINO_STR'] = paying_commitment['MES_TERMINO'].dt.strftime('%m/%Y')

colunas_exibir = [
    'OWNER', 
    'DESCRIPTION', 
    'PARC_ATUAL', 
    'ULTI_PARC', 
    'PARC_REST',
    'VALUE', 
    'GASTO_FUTURO', 
    'ANOMES', 
    'MES_TERMINO_STR'
]

df_paying = paying_commitment[paying_commitment['PARC_REST'] > 0].copy()
df_projecao = df_paying[colunas_exibir].sort_values('MES_TERMINO_STR')

print("=" * 100)
print("PROJEÇÃO DE GASTOS FUTUROS")
print("=" * 100)
print(
    df_projecao 
        .to_string(
            index=False, 
            formatters={
                'VALUE': lambda x: f'R$ {x:.2f}',
                'GASTO_FUTURO': lambda x: f'R$ {x:.2f}'
            }
        )
)

# Totais
total_futuro = df_paying['GASTO_FUTURO'].sum()
data_max = df_paying['MES_TERMINO_STR'].max() if not df_paying.empty else "Nenhuma"
print("\n" + "=" * 100)
print("RESUMO GERAL")
print("=" * 100)
print(f"Total a gastar no futuro: R$ {total_futuro:.2f}")
print(f"Último mês de pagamento: {data_max}")
print(f"Total de compras com parcelas restantes: {len(df_paying)}")

if not df_paying.empty:
    print("\n" + "=" * 100)
    print("RESUMO POR PESSOA (OWNER)")
    print("=" * 100)
    resumo_owner = (
        df_paying
            .groupby('OWNER')
            .agg(
                Total_Gasto_Futuro=('GASTO_FUTURO', 'sum'),
                Quantidade_Compras=('DESCRIPTION', 'count')
            )
            .reset_index()
    )
    resumo_owner['Total_Gasto_Futuro'] = resumo_owner['Total_Gasto_Futuro'].apply(lambda x: f'R$ {x:.2f}')
    print(resumo_owner.to_string(index=False))


print("\n" + "=" * 100)
print("PROJEÇÃO MENSAL DE GASTOS (por mês de competência)")
print("=" * 100)

projecao_mensal = []

for idx, row in paying_commitment.iterrows():
    # Data base da parcela atual
    data_base = row['DATA_ATUAL']
    valor_parcela = row['VALUE']
    parc_atual = row['PARC_ATUAL']
    ult_parc = row['ULTI_PARC']
    
    # Número total de parcelas a partir da atual
    num_parcelas_restantes = ult_parc - parc_atual + 1
    
    # Gera cada mês
    for i in range(num_parcelas_restantes):
        mes_pagamento = data_base + relativedelta(months=i)
        projecao_mensal.append(
            {
                'MES_REFERENCIA': mes_pagamento,
                'VALOR_PARCELA': valor_parcela,
                'DESCRIPTION': row['DESCRIPTION'], 
                'OWNER': row['OWNER']
            }
        )

# Converte para DataFrame
df_mensal = pd.DataFrame(projecao_mensal)

# Agrupa por mês e soma os valores
df_gasto_mensal = (
    df_mensal
        .groupby('MES_REFERENCIA')['VALOR_PARCELA'].sum().reset_index()
    )
df_gasto_mensal = df_gasto_mensal.sort_values('MES_REFERENCIA')

# Formata a coluna de mês para string legível
df_gasto_mensal['MES_STR'] = df_gasto_mensal['MES_REFERENCIA'].dt.strftime('%m/%Y')
df_gasto_mensal['VALOR_PARCELA'] = df_gasto_mensal['VALOR_PARCELA'].round(2)

# Exibe tabela
print(df_gasto_mensal[['MES_STR', 'VALOR_PARCELA']].to_string(index=False, formatters={'VALOR_PARCELA': 'R$ {:.2f}'.format}))

# Total geral de todos os meses (soma das parcelas futuras)
total_geral = df_gasto_mensal['VALOR_PARCELA'].sum()
print(f"\nTotal geral de gastos futuros (incluindo parcela atual): R$ {total_geral:.2f}")

# (Opcional) Gráfico de barras simples se tiver matplotlib instalado
try:
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(14, 6))
    
    meses = df_gasto_mensal['MES_STR']
    valores = df_gasto_mensal['VALOR_PARCELA']
    
    # Plotar barras
    bars = ax.bar(meses, valores, color='skyblue', edgecolor='navy', alpha=0.8)
    
    # Calcular variação percentual em relação ao mês anterior
    variacoes = [None]  # primeiro mês sem variação
    for i in range(1, len(valores)):
        if valores[i-1] > 0:
            pct = (valores[i] - valores[i-1]) / valores[i-1] * 100
        else:
            pct = 0.0
        variacoes.append(pct)
    
    # Adicionar anotações
    for i, (bar, valor) in enumerate(zip(bars, valores)):
        height = bar.get_height()
        
        # 1) Valor TOTAL acima da barra (externo)
        ax.text(bar.get_x() + bar.get_width()/2., height + 15,
                f'R$ {valor:.2f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='black')
        
        # 2) Percentual DENTRO da barra (sem fundo branco)
        if variacoes[i] is not None:
            pct = variacoes[i]
            cor = 'green' if pct >= 0 else 'red'
            sinal = '+' if pct >= 0 else ''
            # Posiciona dentro da barra, a uma pequena distância do topo
            y_text = height - (height * 0.05) if height > 20 else height / 2
            ax.text(bar.get_x() + bar.get_width()/2., y_text,
                    f'{sinal}{pct:.1f}%',
                    ha='center', va='center', fontsize=8, color=cor, fontweight='bold')
    
    # Calcular média dos gastos mensais
    media_valores = valores.mean()
    
    # Adicionar linha horizontal da média
    ax.axhline(y=media_valores, color='orange', linestyle='--', linewidth=2)
    # , label=f'Média: R$ {media_valores:.2f}'

    # Anotação da média (opcional, no canto esquerdo)
    ax.text(0.02, 0.95, f'Média mensal: R$ {media_valores:.2f}',
            transform=ax.transAxes, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.7))
    
    # Total geral como anotação no canto superior direito
    total_geral = valores.sum()
    ax.annotate(f'Total geral: R$ {total_geral:.2f}',
                xy=(0.98, 0.95), xycoords='axes fraction',
                ha='right', va='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="black"),
                fontsize=10, fontweight='bold')
    
    # Configurações dos eixos
    ax.set_xlabel('Mês', fontsize=12)
    ax.set_ylabel('Gasto total (R$)', fontsize=12)
    ax.set_title('Projeção de Gastos Mensais com Parcelas\n(Valor acima, Variação % dentro, Linha média em laranja)', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Ajustar limite superior para caber o rótulo de valor
    max_valor = valores.max()
    ax.set_ylim(0, max_valor + max_valor * 0.12)
        
    # Grid leve
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.show()
    
except ImportError:
    print("\n(Dica: instale o matplotlib com 'pip install matplotlib' para ver o gráfico)") 