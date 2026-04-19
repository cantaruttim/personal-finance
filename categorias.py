## ANÁLISE DAS CATEGORIAS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

categorias = pd.read_excel('./data/relatorio_financeiro_completo.xlsx', sheet_name='sumarizacao_categorias')
print("\n")
print("="*60)
print("DADOS")
print("="*60)
print(categorias)

def plot_top_subcategorias_matplotlib(df, categoria_macro, top_n=5, figsize=(12, 6)):
    """
    Plota um gráfico de barras empilhadas com as top N subcategorias de uma macro categoria.
    Utiliza uma paleta de tons pastéis mais fortes (saturação 0.65, valor 0.9).
    """
    # Filtra pela macro
    df_macro = df[df['categoria_macro'] == categoria_macro].copy()
    if df_macro.empty:
        print(f"⚠️ Nenhum dado encontrado para a categoria macro '{categoria_macro}'")
        return None

    # Ordenação cronológica dos meses
    df_macro['data_ord'] = pd.to_datetime(df_macro['ANOMES'].astype(str).str.zfill(6), format='%m%Y')
    meses_ordenados = sorted(df_macro['data_ord'].unique())
    meses_labels = [d.strftime('%m/%Y') for d in meses_ordenados]

    # Total por subcategoria para selecionar top_n
    total_por_sub = df_macro.groupby('categoria_l2')['VALUE_SUB_CATEGORY'].sum().sort_values(ascending=False)
    top_subcats = total_por_sub.head(top_n).index.tolist()

    # Filtra top subcategorias
    df_top = df_macro[df_macro['categoria_l2'].isin(top_subcats)].copy()

    # Agrupa outras em "Outros"
    outras = df_macro[~df_macro['categoria_l2'].isin(top_subcats)]
    if not outras.empty:
        outras_agg = outras.groupby('data_ord')['VALUE_SUB_CATEGORY'].sum().reset_index()
        outras_agg['categoria_l2'] = 'Outros'
        df_top = pd.concat([df_top, outras_agg], ignore_index=True)

    # Pivot
    pivot = df_top.pivot_table(index='data_ord', columns='categoria_l2', values='VALUE_SUB_CATEGORY',
                               aggfunc='sum', fill_value=0)
    pivot = pivot.reindex(meses_ordenados)

    # Ordenar colunas
    col_order = [c for c in total_por_sub.index if c in pivot.columns]
    if 'Outros' in pivot.columns:
        col_order = [c for c in col_order if c != 'Outros'] + ['Outros']
    pivot = pivot[col_order]

    valores = pivot.values  # shape (n_meses, n_subcats)
    totais_mensais = valores.sum(axis=1)
    subcats = pivot.columns
    n_subcats = len(subcats)

    # Gerar cores pastéis fortes usando HSV com saturação e valor fixos
    hues = np.linspace(0, 1, n_subcats, endpoint=False)
    cores = []
    for h in hues:
        # Converter HSV (h, s=0.65, v=0.9) para RGB
        rgb = mcolors.hsv_to_rgb([h, 0.65, 0.9])
        cores.append(rgb)

    # Plot
    fig, ax = plt.subplots(figsize=figsize)
    bottoms = np.zeros(len(meses_ordenados))
    for i, (sub, cor) in enumerate(zip(subcats, cores)):
        ax.bar(meses_labels, valores[:, i], bottom=bottoms, label=sub, color=cor, alpha=0.9)
        # Anotações de proporção mensal
        for j, (valor, total_mes) in enumerate(zip(valores[:, i], totais_mensais)):
            if valor > 0:
                proporcao = valor / total_mes * 100
                y_pos = bottoms[j] + valor / 2
                ax.text(j, y_pos, f'{proporcao:.0f}%', ha='center', va='center', fontsize=8, color='white', weight='bold')
        bottoms += valores[:, i]

    ax.set_title(f'Despesas por subcategoria - {categoria_macro} (Top {top_n} + Outros)', fontsize=14)
    ax.set_xlabel('Mês/Ano', fontsize=12)
    ax.set_ylabel('Valor (R$)', fontsize=12)
    ax.legend(title='Subcategoria', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Proporções totais
    total_por_subcat = valores.sum(axis=0)
    print("\n" + "="*60)
    print(f"📊 Proporção total de cada subcategoria em '{categoria_macro}' (soma de todos os meses):")
    print("="*60)
    for sub, val in zip(subcats, total_por_subcat):
        perc = val / total_por_subcat.sum() * 100
        print(f"   {sub}: R$ {val:,.2f} ({perc:.1f}%)")
    print("="*60 + "\n")

    plt.show()
    return fig

plot_top_subcategorias_matplotlib(categorias, 'Estilo de Vida')