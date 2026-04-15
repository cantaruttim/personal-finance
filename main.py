import pandas as pd
import re
from config.config import (
    FILE_PATH, 
    FILE_PATH_OUTPUT, 
    FILE_NAME
)
from util.util import (
    ajuste_padrao_anomes, 
    gasto_total_consolidado,
    gasto_total_mensal,
    fillna_zero,
    borrowed_money_by_anomes,
    salva_arquivo_consolidado,
    add_macro_category_fast,
    group_macro_category
)


gastos = pd.read_excel(FILE_PATH, sheet_name='gastos')
gastos = ajuste_padrao_anomes(gastos, 'ANOMES')

print('\n')
print("conferindo valor total mensal ... ")
print(gastos.groupby('ANOMES')['VALUE'].sum())
print('\n')

notmy = borrowed_money_by_anomes(gastos)
notmy = notmy[['ANOMES', 'BORROWED']]
borrowed_grouped = (
    notmy.groupby('ANOMES', as_index=False)['BORROWED'].sum()
)

print('\n')
gastos = gastos.merge(
    borrowed_grouped,
    on='ANOMES',
    how='left'
)

print('\n')

gastos = (
    gasto_total_mensal(
        gastos, 
        'BORROWED', 
        'ANOMES', 
        'VALUE'
    )
)
print("\n")
print("Realizando tratamentos iniciais ...")
df = fillna_zero(gasto_total_consolidado(gastos))

gastos = gastos.drop(columns=['GASTO_MENSAL'])
gastos = gastos.merge(df, on="ANOMES", how="left")

gastos = add_macro_category_fast(gastos)

categories = group_macro_category(gastos)


gastos = gastos.merge(
    categories,
    on=['ANOMES', 'MACRO_CATEGORY'],
    how='left',
    suffixes=('', '_BY_MACRO_CATEGORY')
)

print("\n")
print("Seu relatório está quase pronto ...")
print(gastos)
print("\n")

def clean_dataframe(df):
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df

gastos = clean_dataframe(gastos)



import re
import pandas as pd

def classificar_gasto_cartao(descricao):
    """
    Classifica gastos de cartão de crédito/débito baseado apenas na descrição.
    Retorna: (categoria_macro, categoria_l2, score)
    """
    desc = str(descricao).lower().strip()
    
    # ========== CASOS DIRETOS PRIORITÁRIOS ==========
    casos_diretos = [
        # Assinaturas e serviços digitais
        (r'netflix', 'Estilo de Vida', 'Assinaturas', 0.95),
        (r'spotify', 'Estilo de Vida', 'Assinaturas', 0.95),
        (r'apple\.com|apple bill|applebill', 'Estilo de Vida', 'Assinaturas', 0.95),
        (r'google one|microsoft 365|microsoft', 'Estilo de Vida', 'Assinaturas', 0.9),
        (r'ifood|ifd', 'Estilo de Vida', 'Alimentação', 0.95),
        (r'99food', 'Estilo de Vida', 'Alimentação', 0.95),
        (r'uber.*trip|uber\*', 'Estilo de Vida', 'Mobilidade', 0.95),
        (r'99\*', 'Estilo de Vida', 'Mobilidade', 0.9),
        (r'totalpass|gympass|wellhub', 'Estilo de Vida', 'Saúde/Bem-estar', 0.95),
        
        # Mercados e essenciais
        (r'assai|mercado|supermercado|mercadinho', 'Gastos Essenciais', 'Supermercado', 0.95),
        (r'drogasil|drogaria|farmacia|drog', 'Gastos Essenciais', 'Farmácia', 0.95),
        (r'posto|combust|auto posto', 'Gastos Essenciais', 'Combustível', 0.95),
        
        # Compras online/magazines
        (r'amazon|amazon marketplace', 'Estilo de Vida', 'Compras Online', 0.9),
        (r'mercadolivre', 'Estilo de Vida', 'Compras Online', 0.9),
        (r'magazine luiza|magalu|mlp', 'Estilo de Vida', 'Compras Online', 0.9),
        (r'lojas americanas', 'Estilo de Vida', 'Compras Online', 0.85),
        (r'chillibeans', 'Estilo de Vida', 'Compras', 0.85),

        # Restaurantes e alimentação fora
        (r'outback|restaurante|pizzaria|burger|mc donalds|mcdonalds', 'Estilo de Vida', 'Alimentação', 0.9),
        (r'cafe|cafeteria', 'Estilo de Vida', 'Alimentação', 0.85),
        
        # Serviços financeiros/boletos
        (r'conta vivo|claro|fatura|pg\*', 'Prioridade Financeira', 'Contas', 0.95),
        (r'enel|energia|agua|copel', 'Prioridade Financeira', 'Contas', 0.95),
        (r'iof|juros|multa|encargos', 'Prioridade Financeira', 'Taxas Bancárias', 1.0),
        (r'estorno|reembolso|anul', 'Prioridade Financeira', 'Estorno', 0.95),
        (r'ipva', 'Prioridade Financeira', 'Impostos', 0.95),
        
        # Educação
        (r'anhanguera|college|adai', 'Educação', 'Mensalidade', 0.95),
        
        # Seguros
        (r'zurich|segur', 'Prioridade Financeira', 'Seguro', 0.9),
        
        # Lazer específico
        (r'cinemark|cinema', 'Estilo de Vida', 'Lazer', 0.85),
        (r'park', 'Estilo de Vida', 'Lazer', 0.8),
    ]
    
    for pattern, cat, l2, s in casos_diretos:
        if re.search(pattern, desc):
            return cat, l2, s
    
    # ========== REGRAS POR CATEGORIA COM PONTUAÇÃO ==========
    regras = {
        'Gastos Essenciais': {
            r'mercado|supermercado|mercadinho|assai': 3,
            r'farmacia|drogaria|drogasil': 3,
            r'posto|combust|auto posto': 3,
            r'padaria|acougue': 2,
            r'feira|hort': 2,
        },
        'Estilo de Vida': {
            r'restaurante|pizzaria|burger|lanch|comercio': 2,
            r'cafe|cafeteria|doceria|sucos': 2,
            r'shopping|loja|moda|roupa|calçado': 2,
            r'beleza|estetica|salão|studio|barbearia': 2,
            r'academia|gym|esporte': 2,
            r'cinema|teatro|show|parque': 2,
        },
        'Prioridade Financeira': {
            r'pagamento|conta|boleto|fatura': 3,
            r'seguro|segur': 2,
            r'iof|juros|multa|taxa|encargo': 3,
            r'imposto|ipva|iptu': 3,
        },
        'Educação': {
            r'escola|faculdade|universidade|college|cursos': 3,
            r'livro|material': 2,
        },
        'Saúde': {
            r'clinica|medico|hospital|consulta|exame': 3,
            r'fisioterapia|terapia': 2,
            r'farmacia|drogaria': 2,
        }
    }
    
    scores = {k: 0 for k in regras}
    
    for categoria, patterns in regras.items():
        for pattern, peso in patterns.items():
            if re.search(pattern, desc):
                scores[categoria] += peso
    
    melhor_categoria = max(scores, key=scores.get)
    melhor_score = scores[melhor_categoria]
    
    # ========== FALLBACKS quando não encontrou nada ==========
    if melhor_score == 0:
        # Nomes próprios (pessoas físicas)
        if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', desc) or re.search(r'\d{5,}', desc):
            return 'Outros', 'Pessoa Física', 0.3
        
        # Estabelecimentos genéricos
        if re.search(r'ltda|me$|eireli', desc):
            return 'Outros', 'Estabelecimento Genérico', 0.4
        
        return 'Outros', 'Não Classificado', 0.2
    
    # ========== DEFINE L2 BASEADO NA MELHOR CATEGORIA ==========
    l2_mapping = {
        'Gastos Essenciais': 'Essenciais',
        'Estilo de Vida': 'Lazer/Consumo',
        'Prioridade Financeira': 'Serviços Financeiros',
        'Educação': 'Educação',
        'Saúde': 'Saúde'
    }
    
    score_final = min(1, melhor_score / 5)
    return melhor_categoria, l2_mapping.get(melhor_categoria, 'Outros'), round(score_final, 2)


# ========== APLICAÇÃO NO DATAFRAME gastos ==========
print("Classificando gastos...")
gastos[['categoria_macro', 'categoria_l2', 'score']] = (
    gastos['DESCRIPTION']
        .apply(lambda x: pd.Series(classificar_gasto_cartao(x)))
)

# ========== ANÁLISE DOS "OUTROS" ==========
print("\n" + "="*60)
print("Análise de transações classificadas como 'Outros':")
print("="*60)
outros = gastos[gastos['categoria_macro'] == 'Outros']
if len(outros) > 0:
    print(outros['DESCRIPTION'].value_counts().head(20))
    print(f"\nTotal de 'Outros': {len(outros)} transações ({len(outros)/len(gastos)*100:.1f}%)")
else:
    print("Nenhuma transação classificada como 'Outros'! 🎉")


print("\n✅ Classificação concluída!")
print(f"Distribuição de categorias macro:")
print(gastos['categoria_macro'].value_counts())


salva_arquivo_consolidado(df, FILE_PATH_OUTPUT, FILE_NAME)
salva_arquivo_consolidado(gastos, FILE_PATH_OUTPUT, "finance_personal_report")

# ========== SELEÇÃO DE COLUNAS ==========
# colunas_desejadas = [
#     'bank_id', 'account_type', 'creditDebitType', 'DESCRIPTION',
#     'transactionAmount', 'partiePersonType', 'partieCnpjCpf', 'type',
#     'categoria_macro', 'categoria_l2', 'score'
# ]

# gastos = gastos[
#     [col for col in colunas_desejadas if col in gastos.columns]
# ]
