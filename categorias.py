## ANÁLISE DAS CATEGORIAS
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

categorias = pd.read_excel('./data/relatorio_financeiro_completo.xlsx', sheet_name='sumarizacao_categorias')
print("\n")
print("="*60)
print("DADOS")
print("="*60)
print(categorias)

def salvar_imagem(fig, nome_arquivo, caminho="./util/graficos/", dpi=300, bbox_inches='tight'):
    import os

    os.makedirs(caminho, exist_ok=True)
    
    caminho_completo = os.path.join(caminho, nome_arquivo)
    print(f"Salvando imagem: {caminho_completo}")
    
    fig.savefig(caminho_completo, dpi=dpi, bbox_inches=bbox_inches)
    print("✅ Imagem salva com sucesso!")


def plot_top_subcategorias_matplotlib(df, categoria_macro, top_n=5, figsize=(12, 6)):
    """
    Plota um gráfico de barras empilhadas com as top N subcategorias.
    Utiliza paleta 'tab10' e texto com fundo preto semitransparente para máxima legibilidade.
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

    # Filtra apenas as top subcategorias
    df_top = df_macro[df_macro['categoria_l2'].isin(top_subcats)]

    # Pivot
    pivot = (
        df_top
            .pivot_table(
                index='data_ord', 
                columns='categoria_l2', 
                values='VALUE_SUB_CATEGORY',
                aggfunc='sum', 
                fill_value=0
            )
    )
    pivot = pivot.reindex(meses_ordenados)

    # Ordenar colunas por valor total decrescente
    col_order = [c for c in total_por_sub.index if c in pivot.columns]
    pivot = pivot[col_order]

    valores = pivot.values
    totais_mensais = valores.sum(axis=1)
    subcats = pivot.columns
    n_subcats = len(subcats)

    cmap = plt.get_cmap('tab10')
    cores = [cmap(i % 10) for i in range(n_subcats)]

    # Plot
    fig, ax = plt.subplots(figsize=figsize)
    bottoms = np.zeros(len(meses_ordenados))

    for i, (sub, cor) in enumerate(zip(subcats, cores)):
        ax.bar(meses_labels, valores[:, i], bottom=bottoms, label=sub, color=cor,
               alpha=0.85, edgecolor='black', linewidth=0.5)
        # Anotações com valor e porcentagem
        for j, (valor, total_mes) in enumerate(zip(valores[:, i], totais_mensais)):
            if valor > 0:
                proporcao = valor / total_mes * 100
                y_pos = bottoms[j] + valor / 2
                texto = f'R$ {valor:,.2f}\n({proporcao:.0f}%)'
                # Fundo preto semitransparente para contraste
                ax.text(j, y_pos, texto, ha='center', va='center', fontsize=7,
                        color='white', weight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.6))
        bottoms += valores[:, i]

    ax.set_title(f'Despesas por subcategoria - {categoria_macro} (Top {top_n})', fontsize=14)
    ax.set_ylabel('Valor (R$)', fontsize=12)
    ax.legend(title='Subcategoria', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Proporções totais (console)
    total_por_subcat = valores.sum(axis=0)
    print("\n" + "="*60)
    print(f"📊 Proporção total das top {top_n} subcategorias em '{categoria_macro}':")
    print("="*60)
    for sub, val in zip(subcats, total_por_subcat):
        perc = val / total_por_subcat.sum() * 100
        print(f"   {sub}: R$ {val:,.2f} ({perc:.1f}%)")
    print("="*60 + "\n")
    
    salvar_imagem(fig, 'categoria_subcat.png')
    plt.show()
    return fig

plot_top_subcategorias_matplotlib(categorias, 'Estilo de Vida')