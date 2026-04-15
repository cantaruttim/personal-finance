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

def salvar_imagem(fig, nome_arquivo, caminho="./data/graficos/", dpi=300, bbox_inches='tight'):
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


# ========== GERAR GRÁFICOS ==========
print("\n" + "="*60)
print("Gerando gráficos...")
print("="*60)
grafico_um(df)
grafico_dois(df)
grafico_dois_um(df)
grafico_dois_dois(df)