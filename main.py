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
    salva_multiplas_abas
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

print("\n")
print("Seu relatório está quase pronto ...")
print(gastos)
print("\n")

def clean_dataframe(df):
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df

gastos = clean_dataframe(gastos)


def classificar_gasto_cartao(descricao):
    """
    
        Pipeline que classifica gastos de cartão de crédito/débito baseado apenas na descrição.
        Retorna: (categoria_macro, categoria_l2, score) para as descrições passadas pelo classificador
    
    """
    desc = str(descricao).lower().strip()
    
    # ========== PRÉ-PROCESSAMENTO ==========
    # Remove qualquer padrão de parcela/data do tipo "01/02", "02/02", etc.
    desc = re.sub(r'\d{2}/\d{2}', '', desc)
    desc = re.sub(r'\s+', ' ', desc)
    desc = desc.strip()
    
    # Remove prefixos comuns de gateway (mas preserva parte relevante)
    desc = re.sub(r'^(mp\*|asaas\*|zp\*|hna\*|pg\*|jim\.com\s*)', '', desc)
    
    # ========== CASOS DIRETOS PRIORITÁRIOS ==========
    # (Organizados: primeiro específicos de categorias, depois transferências)
    casos_diretos = [
        # --- CONDOMÍNIO ---
        (r'pgconta hubert imo', 'Residência', 'Condomínio', 1.0),
        (r'pgconta.*imo|condominio', 'Residência', 'Condomínio', 0.95),
        (r'bancobradescosa', 'Residência', 'Condomínio', 1.0),
        
        # --- ASSINATURAS E SERVIÇOS DIGITAIS ---
        (r'netflix', 'Estilo de Vida', 'Assinaturas', 0.95),
        (r'helphbomaxcom', 'Estilo de Vida', 'Assinaturas - Streaming', 0.95),
        (r'spotify', 'Estilo de Vida', 'Assinaturas', 0.95),
        (r'apple\.com|apple bill|applebill|applecombill|allsignature', 'Estilo de Vida', 'Assinaturas', 0.95),
        (r'google one|microsoft 365|microsoft', 'Estilo de Vida', 'Assinaturas', 0.9),
        (r'ifood|ifd', 'Estilo de Vida', 'Alimentação', 0.95),
        (r'99food', 'Estilo de Vida', 'Alimentação', 0.95),
        (r'uber.*trip|uber\*', 'Estilo de Vida', 'Mobilidade', 0.95),
        (r'99\*', 'Estilo de Vida', 'Mobilidade', 0.9),
        (r'totalpass|gympass|wellhub|nazareias|sports', 'Estilo de Vida', 'Saúde & Bem-estar', 0.95),
        (r'azul linhas aereas bras|accor|mino|melimais|livelo|ig\*', 'Estilo de Vida', 'Pontos & Viagens', 0.95),
        (r'envio mens.automatica', 'Estilo de Vida', 'Serviços Financeiros', 0.95),
        (r'cod3rs', 'Estilo de Vida', 'Mentoria & Carreira', 0.95),
        (r'pg \*coders club', 'Estilo de Vida', 'Mentoria & Carreira', 0.95),
        
        # --- TRANSPORTE PÚBLICO ---
        (r'bilheteunicosaopaulo', 'Gastos Essenciais', 'Transporte Público', 0.95),
        
        # --- MERCADOS E ESSENCIAIS ---
        (r'assai|mercado|supermercado|mercadinho|jmhonestmarket|top ovos', 'Gastos Essenciais', 'Supermercado', 0.95),
        (r'drogasil|drogaria|farmacia|mendonca farma|drog|raia280|metro farma', 'Gastos Essenciais', 'Farmácia', 0.95),
        (r'posto|combust|auto posto|centroautomotivoe|auto p b 2 ltda|sol dourado auto servi', 'Gastos Essenciais', 'Combustível', 0.95),
        (r'vitrine do oleo|gp servicos automo|centauro ce165|m v derivados', 'Automóvel', 'Manutenção', 0.95),
        (r'franciscobatistaa', 'Residência', 'Manutenção', 0.95),
        (r'estapar', 'Automóvel', 'Estacionamento', 0.95),
        (r'marmitaria', 'Gastos Essenciais', 'Marmitas', 0.95),
        (r'astor comercio de alime', 'Gastos Essenciais', 'Mercearia', 0.85),
        
        # --- COMPRAS ONLINE / MAGAZINES ---
        (r'amazon|amazon marketplace', 'Estilo de Vida', 'Compras Online', 0.9),
        (r'oboticario', 'Estilo de Vida', 'Compras Online', 0.9),
        (r'mercadolivre', 'Estilo de Vida', 'Compras Online', 0.9),
        (r'magazine luiza|magalu|mlp', 'Estilo de Vida', 'Compras Online', 0.9),
        (r'lojas americanas', 'Estilo de Vida', 'Compras Online', 0.85),
        (r'decathlon', 'Estilo de Vida', 'Esportes', 0.85),
        (r'chillibeans', 'Estilo de Vida', 'Compras', 0.85),
        
        # --- DOAÇÕES E IGREJAS ---
        (r'ass de deus min ipiran', 'Estilo de Vida', 'Doações', 0.85),
        (r'ipiranga', 'Estilo de Vida', 'Doações', 0.8),
        
        # --- RESTAURANTES E ALIMENTAÇÃO FORA ---
        (r'outback|restaurante|pizzaria|burger|mc donalds|mcdonalds|63430674geovanna', 'Estilo de Vida', 'Alimentação', 0.9),
        (r'cafe|cafeteria|emporio amino|doces|37773965faiane|fini|brasil cacau|doceria contem amor|chocolandia|picole sabore mix|senhorita food truck|vivano steak|viena express shopping|tutti frutti|papa dominico mooca|big bread|santa monica paes', 'Estilo de Vida', 'Doces & Padaria', 0.85),
        (r'bocado gastronomia|fun funchal', 'Estilo de Vida', 'Alimentação', 0.85),
        
        # --- BELEZA E ESTÉTICA ---
        (r'd clinic estetica|almeida studio ha|barbearianovoesti|mp*ciadabeleza|makibella shop', 'Estilo de Vida', 'Beleza & Estética', 0.9),
        
        # --- LAZER ---
        (r'cinemark|cinema', 'Estilo de Vida', 'Lazer', 0.85),
        (r'action park|rivera beachentennis ltd|century a park estacio|pierry park|deck ipiranga beach sp', 'Estilo de Vida', 'Lazer', 0.85),
        
        # --- SERVIÇOS FINANCEIROS / BOLETOS ---
        (r'conta vivo|recvivo|claro|fatura|pg\*', 'Prioridade Financeira', 'Contas', 0.95),
        (r'loteriasonline', 'Estilo de Vida', 'Lotérica', 0.95),
        (r'enel|energia|agua|copel', 'Prioridade Financeira', 'Contas', 0.95),
        (r'iof|juros|multa|encargos|anuidade diferenci', 'Prioridade Financeira', 'Taxas Bancárias', 1.0),
        (r'estorno|reembolso|anul', 'Prioridade Financeira', 'Estorno', 0.95),
        (r'ipva|detransp|simplesnacional', 'Prioridade Financeira', 'Impostos', 0.95),
        (r'paygo|asaas\*|ebte', 'Prioridade Financeira', 'Serviços Financeiros', 0.9),
        (r'pgconta(?!.*hubert)', 'Prioridade Financeira', 'Pagamento de Contas', 0.9),
        (r'zp\*', 'Prioridade Financeira', 'Serviços Financeiros', 0.8),
        (r'mp\*', 'Prioridade Financeira', 'Pagamento Online', 0.85),
        
        # --- EDUCAÇÃO ---
        (r'anhanguera ed|adaicollege|dio|htm\*adai college', 'Educação', 'Mensalidade', 0.95),
        (r'ana?ju?h', 'Educação', 'Identidade Visual / Marketing', 0.95),
        
        # --- SEGUROS ---
        (r'zurich|segur', 'Prioridade Financeira', 'Seguro', 0.9),
        
        # --- VIAGENS (aéreas) ---
        (r'gol linhas a\*gnef', 'Estilo de Vida', 'Passagens Aéreas', 0.95),
        
        # --- UTILIDADES DOMÉSTICAS ---
        (r'siciliano utensili', 'Estilo de Vida', 'Utilidades Domésticas', 0.85),
        (r'pare azul', 'Automóvel', 'Estacionamento', 0.9),
        
        # --- TRANSFERÊNCIAS A PESSOAS (FALLBACK - apenas se nada acima casou) ---
        (r'jim\.com', 'Prioridade Financeira', 'Transferência a Pessoa', 0.9),
        (r'[a-z]+\s+[a-z]+\s+[a-z]+', 'Prioridade Financeira', 'Transferência a Pessoa', 0.7),
        (r'^[a-z]+\s+[a-z]+$', 'Prioridade Financeira', 'Transferência a Pessoa', 0.65),
        (r'\d{5,}\.?\d*', 'Prioridade Financeira', 'Transferência (CPF)', 0.8),
    ]
    
    for pattern, cat, l2, s in casos_diretos:
        if re.search(pattern, desc):
            return cat, l2, s
    
    # ========== REGRAS POR CATEGORIA COM PONTUAÇÃO ==========
    regras = {
        'Gastos Essenciais': {
            r'mercado|supermercado|mercadinho|assai|comercio de alimentos|mercearia': 3,
            r'farmacia|drogaria|drogasil|raia|metro farma': 3,
            r'posto|combust|auto posto|shell|ipiranga': 3,
            r'padaria|acougue|paes|bread': 2,
            r'feira|hort|fruta': 2,
        },
        'Estilo de Vida': {
            r'restaurante|pizzaria|burger|lanch|comercio de alimentos preparados': 2,
            r'cafe|cafeteria|doceria|sucos|sorvete|chocolate': 2,
            r'shopping|loja|moda|roupa|calçado|makibella|americanas': 2,
            r'beleza|estetica|salão|studio|barbearia|cosméticos': 2,
            r'academia|gym|esporte|decathlon|fitness': 2,
            r'cinema|teatro|show|parque|entretenimento': 2,
        },
        'Prioridade Financeira': {
            r'pagamento|conta|boleto|fatura|pgconta|asaas': 3,
            r'seguro|segur|zurich': 2,
            r'iof|juros|multa|taxa|encargo|anuidade': 3,
            r'imposto|ipva|iptu|detran|simples nacional': 3,
            r'transferência|pix|envio|recebimento': 2,
        },
        'Educação': {
            r'escola|faculdade|universidade|college|cursos|anhanguera|adai|dio': 3,
            r'livro|material|cod3rs|mentoria|identidade visual': 2,
        },
        'Saúde': {
            r'clinica|medico|hospital|consulta|exame|fisioterapia|terapia': 3,
            r'farmacia|drogaria': 2,
        },
        'Automóvel': {
            r'auto servi|manutenção|oleo|derivados|centro automotivo|estapar|estacionamento': 3,
            r'peças|oficina': 2,
        },
        'Residência': {
            r'franciscobatistaa|hubert imoveis|condomínio|aluguel': 3,
            r'reforma|construção': 2,
        }
    }
    
    scores = {k: 0 for k in regras}
    
    for categoria, patterns in regras.items():
        for pattern, peso in patterns.items():
            if re.search(pattern, desc):
                scores[categoria] += peso
    
    melhor_categoria = max(scores, key=scores.get)
    melhor_score = scores[melhor_categoria]
    
    # ========== FALLBACKS ==========
    if melhor_score == 0:
        # Nomes próprios (pessoas físicas) - classifica como transferência
        if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', desc) or re.search(r'\d{5,}', desc):
            return 'Prioridade Financeira', 'Transferência a Pessoa', 0.7
        
        # Estabelecimentos com CNPJ ou razão social genérica
        if re.search(r'ltda|me$|eireli|comercio|serviços', desc):
            return 'Outros', 'Estabelecimento Genérico', 0.4
        
        # Nomes curtos sem padrão (ex: MK)
        if len(desc) < 10:
            return 'Outros', 'Não Classificado', 0.2
        
        return 'Outros', 'Não Classificado', 0.2
    
    # ========== DEFINE L2 ==========
    l2_mapping = {
        'Gastos Essenciais': 'Essenciais',
        'Estilo de Vida': 'Lazer/Consumo',
        'Prioridade Financeira': 'Serviços Financeiros',
        'Educação': 'Educação',
        'Saúde': 'Saúde',
        'Automóvel': 'Automóvel',
        'Residência': 'Residência'
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


abas = {
    "consolidado_por_mes": df,                    
    "detalhamento_gastos": gastos,                
    "resumo_emprestimos": borrowed_grouped,       
}

# Salva tudo em um único arquivo
salva_multiplas_abas(abas, FILE_PATH_OUTPUT, "relatorio_financeiro_completo")