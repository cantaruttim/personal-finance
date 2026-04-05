from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def select_columns(df, columns: list):
    """
    Seleciona uma lista de colunas de maneira dinâmica
    """
    return df[columns].drop_duplicates()

def grafico_um(df):
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
        ax2.plot(x, y_linha, marker='o', color='red', linewidth=2)

    plt.title('Gasto Mensal e Percentual de Variação')

    print("Salvando imagem ... ")
    fig.savefig(
        "./data/graficos/grafico_um.png", 
        dpi=300, 
        bbox_inches='tight'
    )

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


df = pd.read_excel("./data/finance_personal_report.xlsx")
df = df[['ANOMES', 'MACRO_CATEGORY', 'VALUE_BY_MACRO_CATEGORY']]
df = df[~df['MACRO_CATEGORY'].isin(["OUTROS", "EMPRÉSTIMOS"])]

def prepare_macro_data(df):
    grouped = (
        df.groupby(['ANOMES', 'MACRO_CATEGORY'])['VALUE_BY_MACRO_CATEGORY']
        .sum()
        .reset_index()
    )

    pivot_df = grouped.pivot(
        index='ANOMES',
        columns='MACRO_CATEGORY',
        values='VALUE_BY_MACRO_CATEGORY'
    ).fillna(0)

    return pivot_df

def macro_percentage(df):
    pivot_df = prepare_macro_data(df)

    percent_df = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100

    return percent_df.reset_index()


def grafico_dois(df):
    pivot_df = prepare_macro_data(df)

    pivot_df.plot(kind='bar')

    plt.xlabel('ANOMES')
    plt.ylabel('Valor')
    plt.title('Gastos por Macro Categoria')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(
        "./data/graficos/grafico_dois.png", 
        dpi=300, 
        bbox_inches='tight'
    )
    plt.show()


def grafico_dois_um(df):
    pivot_df = prepare_macro_data(df)

    pivot_df.plot(kind='bar', stacked=True)

    plt.xlabel('ANOMES')
    plt.ylabel('Valor')
    plt.title('Evolução de Gastos (Stacked)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(
        "./data/graficos/grafico_dois_um.png", 
        dpi=300, 
        bbox_inches='tight'
    )
    plt.show()

def grafico_dois_dois(df):
    percent_df = macro_percentage(df).set_index('ANOMES')

    percent_df.plot(kind='bar', stacked=True)

    plt.xlabel('ANOMES')
    plt.ylabel('%')
    plt.title('Distribuição Percentual por Macro Categoria')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(
        "./data/graficos/grafico_dois_dois.png", 
        dpi=300, 
        bbox_inches='tight'
    )
    plt.show()


grafico_dois(df)
grafico_dois_um(df)
grafico_dois_dois(df)