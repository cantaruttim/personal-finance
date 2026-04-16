from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_excel("./data/relatorio_financeiro_completo.xlsx", sheet_name="detalhamento_gastos")

def prepare_macro_data(df):
    """
    Agrupa os gastos por ANOMES e categoria_macro, somando os valores.
    Retorna um DataFrame pivotado com meses nas linhas e categorias nas colunas.
    """
    grouped = (
        df.groupby(['ANOMES', 'categoria_macro'])['VALUE']
        .sum()
        .reset_index()
    )
    pivot_df = grouped.pivot(
        index='ANOMES',
        columns='categoria_macro',
        values='VALUE'
    ).fillna(0)
    return pivot_df

def prepare_macro_n2_data(df):
    """
    Agrupa por ANOMES, categoria_macro e categoria_l2.
    Retorna pivot com multi-índice nas colunas.
    """
    grouped = (
        df.groupby(['ANOMES', 'categoria_macro', 'categoria_l2'])['VALUE']
        .sum()
        .reset_index()
    )
    pivot_df = grouped.pivot(
        index='ANOMES',
        columns=['categoria_macro', 'categoria_l2'],
        values='VALUE'
    ).fillna(0)
    return pivot_df

def macro_percentage(df):
    """
    Calcula a participação percentual de cada categoria_macro por mês.
    """
    pivot_df = prepare_macro_data(df)
    percent_df = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100
    return percent_df.reset_index()

def salvar_imagem(fig, nome_arquivo, caminho="./util/graficos/", dpi=300, bbox_inches='tight'):
    import os

    os.makedirs(caminho, exist_ok=True)
    
    caminho_completo = os.path.join(caminho, nome_arquivo)
    print(f"Salvando imagem: {caminho_completo}")
    
    fig.savefig(caminho_completo, dpi=dpi, bbox_inches=bbox_inches)
    print("✅ Imagem salva com sucesso!")


def select_columns(df, columns: list):
    """
    Seleciona uma lista de colunas de maneira dinâmica
    """
    return df[columns].drop_duplicates()


def grafico_um(df):
    print("Gráfico 1: Gasto Mensal e Variação Percentual\n")

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
    perc = df1['PERC_VARIACAO']

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(x, y, color='steelblue')
    
    # Remove o eixo Y (inclui ticks e rótulo)    
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)

    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_title('Gasto Mensal e Variação Percentual')


    # Anotar valores das barras
    for bar in bars:
        height = bar.get_height()
        if height > max(y) * .05:
            cor = 'white'
            offset = -5
            va = 'top'
        else:
            cor = 'black'
            offset = 5
            va = 'bottom'
            
        ax.annotate(
            f'R$ {height:,.2f}',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, offset),
            textcoords="offset points",
            ha='center',
            va=va,
            color=cor,
            fontweight='bold'
        )

    # Anotar variação percentual
    for bar, p in zip(bars, perc):
        if pd.notna(p):
            sign = '+' if p >= 0 else ''
            text = f'{sign}{p:.1f}%'
            y_pos = bar.get_height() + (bar.get_height() * 0.02) if p >= 0 else bar.get_height() - (bar.get_height() * 0.05)
            if y_pos > max(y) * 1.1:
                y_pos = max(y) * 1.05
            if y_pos < 0:
                y_pos = 0
            ax.text(bar.get_x() + bar.get_width()/2, y_pos, text,
                    ha='center', va='bottom' if p>=0 else 'top',
                    fontsize=9, color='red' if p<0 else 'green',
                    fontweight='bold')

    plt.xticks(rotation=45)
    plt.tight_layout()
    
    salvar_imagem(fig, "grafico_um.png")
    plt.show()


def grafico_dois(df):
    """
    Gráfico de barras agrupadas (não empilhadas) por categoria macro.
    """
    pivot_df = prepare_macro_data(df)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    pivot_df.plot(kind='bar', ax=ax, legend=True)
    
    # Remove eixo Y e spines desnecessários
    ax.get_yaxis().set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel('Ano/Mês')
    ax.set_title('Gastos por Macro Categoria')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Anotar valores nas barras (opcional, mas pode ser útil)
    for container in ax.containers:
        ax.bar_label(container, fmt='R$ %.2f', fontsize=8, padding=3)
    
    salvar_imagem(fig, "grafico_dois.png")
    plt.show()

def grafico_dois_um(df):
    """
    Gráfico de barras empilhadas (stacked) por categoria macro.
    """
    pivot_df = prepare_macro_data(df)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    pivot_df.plot(kind='bar', stacked=True, ax=ax, legend=True)
    
    ax.get_yaxis().set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel('Ano/Mês')
    ax.set_title('Evolução de Gastos (Stacked)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Anotar valores totais no topo de cada barra empilhada
    for i, (idx, row) in enumerate(pivot_df.iterrows()):
        total = row.sum()
        if total > 0:
            ax.text(i, total, f'R$ {total:,.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    salvar_imagem(fig, "grafico_dois_um.png")
    plt.show()

def grafico_dois_dois(df):
    """
    Gráfico de barras empilhadas mostrando a distribuição percentual por categoria macro.
    """
    percent_df = macro_percentage(df).set_index('ANOMES')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    percent_df.plot(kind='bar', stacked=True, ax=ax, legend=True)
    
    ax.get_yaxis().set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel('Ano/Mês')
    ax.set_ylabel('%')  # Mantém o título do eixo Y, mas sem os ticks (opcional)
    ax.set_title('Distribuição Percentual por Macro Categoria')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Anotar valores percentuais dentro das barras (opcional)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', fontsize=8, label_type='center')
    
    salvar_imagem(fig, "grafico_dois_dois.png")
    plt.show()

def grafico_macro_evolucao(df):
    """
    Gráfico de linhas mostrando a evolução dos gastos por macro categoria ao longo dos meses.
    """
    # Prepara os dados pivotados (meses nas linhas, categorias nas colunas)
    pivot_df = prepare_macro_data(df)  # já retorna DataFrame com index=ANOMES
    
    # Ordenar cronologicamente (caso ANOMES seja string 'MMYYYY')
    pivot_df.index = pd.to_datetime(pivot_df.index, format='%m%Y')
    pivot_df = pivot_df.sort_index()
    pivot_df.index = pivot_df.index.strftime('%b/%Y')  # rótulos bonitos
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plotar linhas com marcadores
    pivot_df.plot(kind='line', marker='o', ax=ax, linewidth=2, markersize=6, legend=True)
    
    # Remover eixo Y e spines laterais
    ax.get_yaxis().set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel('Ano/Mês')
    ax.set_title('Evolução dos Gastos por Macro Categoria')
    plt.xticks(rotation=45)
    
    # Legenda posicionada fora para não atrapalhar
    plt.legend(title='Categoria Macro', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # (Opcional) Anotar valores nos pontos (útil para poucos meses)
    for line in ax.lines:
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            if y > 0:
                ax.annotate(f'R$ {y:,.0f}', (x, y), textcoords="offset points",
                            xytext=(0, 10), ha='center', fontsize=8)
    
    salvar_imagem(fig, "grafico_macro_evolucao.png")
    plt.show()    

def grafico_sub_evolucao(df, macro_filter=None, top_n=None):
    """
    Gráfico de linhas mostrando a evolução dos gastos por subcategoria (categoria_l2).
    
    Parâmetros:
        - df: DataFrame com colunas 'ANOMES', 'categoria_macro', 'categoria_l2', 'VALUE'
        - macro_filter: (opcional) nome da macro categoria para filtrar (ex: 'Estilo de Vida')
        - top_n: (opcional) número de subcategorias com maior gasto total para exibir
    """
    # Copia para não alterar original
    data = df.copy()
    
    # Filtra por macro categoria se necessário
    if macro_filter:
        data = data[data['categoria_macro'] == macro_filter]
        titulo = f"Evolução dos Gastos por Subcategoria - {macro_filter}"
    else:
        titulo = "Evolução dos Gastos por Subcategoria"
    
    # Agrupa por ANOMES e categoria_l2
    grouped = data.groupby(['ANOMES', 'categoria_l2'])['VALUE'].sum().reset_index()
    
    # Se top_n for especificado, calcula totais por subcategoria e filtra
    if top_n:
        total_por_sub = grouped.groupby('categoria_l2')['VALUE'].sum().sort_values(ascending=False)
        top_subcats = total_por_sub.head(top_n).index
        grouped = grouped[grouped['categoria_l2'].isin(top_subcats)]
    
    # Pivot: linhas = ANOMES, colunas = categoria_l2
    pivot_df = grouped.pivot(index='ANOMES', columns='categoria_l2', values='VALUE').fillna(0)
    
    # Ordenar cronologicamente
    pivot_df.index = pd.to_datetime(pivot_df.index, format='%m%Y')
    pivot_df = pivot_df.sort_index()
    pivot_df.index = pivot_df.index.strftime('%b/%Y')
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plotar linhas com marcadores
    pivot_df.plot(kind='line', marker='o', ax=ax, linewidth=2, markersize=6, legend=True)
    
    # Remover eixo Y e spines laterais
    ax.get_yaxis().set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel('Ano/Mês')
    ax.set_title(titulo)
    plt.xticks(rotation=45)
    
    # Legenda posicionada fora
    plt.legend(title='Subcategoria', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Anotar valores nos pontos (opcional)
    for line in ax.lines:
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            if y > 0:
                ax.annotate(f'R$ {y:,.0f}', (x, y), textcoords="offset points",
                            xytext=(0, 10), ha='center', fontsize=7)
    
    salvar_imagem(fig, "grafico_sub_evolucao.png")
    plt.show()

# ========== GERAR GRÁFICOS ==========
print("\n" + "="*60)
print("Gerando gráficos...")
print("="*60)
grafico_um(df)
grafico_dois(df)
grafico_dois_um(df)
grafico_dois_dois(df)
grafico_macro_evolucao(df)
grafico_sub_evolucao(df, top_n=3)