import pdfplumber
import pandas as pd
import re
from datetime import datetime
from collections import Counter

# -------------------------------
# 1. Extrair e parsear linhas do extrato
# -------------------------------
def extrair_transacoes(caminho_pdf):
    """
    Extrai as transações do extrato do Itaú.
    Retorna lista de dicionários com: data, descricao, valor, saldo (quando disponível)
    """
    transacoes = []
    saldo_por_data = {}  # guarda o saldo final de cada dia
    lancamentos_por_data = {}  # guarda lista de (descricao, valor) por data

    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            linhas = text.split('\n')
            for linha in linhas:
                # Procura linha que começa com data (dd/mm/aaaa)
                match = re.match(r'(\d{2}/\d{2}/\d{4})\s+(.+)', linha.strip())
                if not match:
                    continue
                data_str, resto = match.groups()
                data = datetime.strptime(data_str, '%d/%m/%Y')
                
                # Separa a descrição do valor (o valor é o último campo)
                # Exemplos:
                # "SALDO DO DIA -58,27"
                # "PIX TRANSF Gabriel09/01 17.000,00"
                # "FATURA PAGA AZUL ITAU IN -17.773,64"
                # O valor pode ter ponto de milhar e vírgula decimal
                
                # Tenta encontrar um número no final da linha (pode ter sinal)
                valor_match = re.search(r'(-?\d{1,3}(?:\.\d{3})*,\d{2})\s*$', resto)
                if not valor_match:
                    continue  # linha sem valor (improvável)
                
                valor_str = valor_match.group(1)
                # Remove pontos de milhar e troca vírgula por ponto
                valor_str = valor_str.replace('.', '').replace(',', '.')
                valor = float(valor_str)
                
                # Descrição é o texto antes do valor
                descricao = resto[:valor_match.start()].strip()
                
                # Se for SALDO DO DIA, guarda separadamente
                if descricao.upper() == "SALDO DO DIA":
                    saldo_por_data[data] = valor
                else:
                    # Remove sujeira como "09/01" grudado no nome (ex: "Gabriel09/01")
                    descricao_limpa = re.sub(r'\d{2}/\d{4}', '', descricao).strip()
                    if data not in lancamentos_por_data:
                        lancamentos_por_data[data] = []
                    lancamentos_por_data[data].append((descricao_limpa, valor))
    
    # Agora monta a lista final de transações, associando cada lançamento ao saldo do dia (se disponível)
    for data, lancamentos in lancamentos_por_data.items():
        saldo = saldo_por_data.get(data, None)
        for desc, val in lancamentos:
            transacoes.append({
                'data': data,
                'descricao': desc,
                'valor': val,
                'saldo': saldo
            })
    
    # Ordena por data
    transacoes.sort(key=lambda x: x['data'])
    return transacoes

# -------------------------------
# 2. Categorização e análise (igual ao anterior, adaptado para None no saldo)
# -------------------------------
def categorizar_descricao(desc):
    desc_upper = desc.upper()
    if 'PIX TRANSF' in desc_upper:
        return 'PIX'
    elif 'TED' in desc_upper:
        return 'TED'
    elif 'FATURA PAGA' in desc_upper:
        return 'PAGAMENTO FATURA'
    elif 'TAR PACOTE' in desc_upper:
        return 'TAXA BANCARIA'
    elif 'FINANC IMOBILIARIO' in desc_upper:
        return 'FINANCIAMENTO'
    elif 'SEGURO CARTAO' in desc_upper:
        return 'SEGURO'
    elif 'DA PMSP' in desc_upper:
        return 'TAXA/IMPOSTO'
    elif 'REND PAGO APLIC AUT MAIS' in desc_upper:
        return 'RENDIMENTO'
    elif 'IOF' in desc_upper:
        return 'IMPOSTO'
    elif 'PAGTO Multa de Veículo' in desc_upper:
        return 'MULTA'
    elif 'INT /SIMPLES NACIONA' in desc_upper:
        return 'IMPOSTO'
    else:
        return 'OUTROS'

def analisar_transacoes(transacoes):
    df = pd.DataFrame(transacoes)
    if df.empty:
        return df, {}
    df['tipo'] = df['valor'].apply(lambda x: 'Crédito' if x > 0 else 'Débito')
    df['categoria'] = df['descricao'].apply(categorizar_descricao)
    
    total_credito = df[df['valor'] > 0]['valor'].sum()
    total_debito = df[df['valor'] < 0]['valor'].sum()
    num_transacoes = len(df)
    
    # Saldo inicial e final: tenta pegar do primeiro e último saldo disponível
    df_com_saldo = df.dropna(subset=['saldo'])
    if not df_com_saldo.empty:
        saldo_inicial = df_com_saldo.iloc[0]['saldo'] - df_com_saldo.iloc[0]['valor']  # aproximado
        saldo_final = df_com_saldo.iloc[-1]['saldo']
    else:
        saldo_inicial = saldo_final = None
    
    cat_credito = df[df['valor'] > 0].groupby('categoria')['valor'].sum().sort_values(ascending=False)
    cat_debito = df[df['valor'] < 0].groupby('categoria')['valor'].sum().sort_values()
    
    # Top contrapartes
    contrapartes = []
    for _, row in df.iterrows():
        desc = row['descricao'].upper()
        if 'PIX TRANSF' in desc or 'TED' in desc:
            resto = re.sub(r'(PIX TRANSF|TED)', '', desc).strip()
            if resto:
                contrapartes.append(resto)
    top_contrapartes = Counter(contrapartes).most_common(5)
    
    resumo = {
        'Período': f"{df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}",
        'Saldo inicial (R$)': saldo_inicial,
        'Saldo final (R$)': saldo_final,
        'Total créditos (R$)': total_credito,
        'Total débitos (R$)': abs(total_debito),
        'Variação líquida (R$)': total_credito + total_debito,
        'Número de transações': num_transacoes,
        'Maior crédito (R$)': df['valor'].max(),
        'Maior débito (R$)': df['valor'].min(),
        'Categorias com maior crédito': cat_credito.head(3).to_dict(),
        'Categorias com maior débito': cat_debito.head(3).to_dict(),
        'Principais contrapartes': top_contrapartes
    }
    return df, resumo

def exportar_csv(df, nome_arquivo='transacoes_analisadas.csv'):
    df_export = df.copy()
    df_export['data'] = df_export['data'].dt.strftime('%d/%m/%Y')
    df_export['valor'] = df_export['valor'].apply(lambda x: f"{x:.2f}")
    df_export['saldo'] = df_export['saldo'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    df_export.to_csv(nome_arquivo, index=False, sep=';', encoding='utf-8-sig')
    print(f"✅ Transações exportadas para '{nome_arquivo}'")

def imprimir_resumo(resumo):
    print("\n" + "="*60)
    print("📊 RESUMO FINANCEIRO DO EXTRATO")
    print("="*60)
    for chave, valor in resumo.items():
        if chave in ['Categorias com maior crédito', 'Categorias com maior débito', 'Principais contrapartes']:
            print(f"\n{chave}:")
            if isinstance(valor, dict):
                for k, v in valor.items():
                    print(f"  - {k}: R$ {v:.2f}")
            else:
                for nome, qtd in valor:
                    print(f"  - {nome}: {qtd} transações")
        else:
            if isinstance(valor, float):
                print(f"{chave}: R$ {valor:.2f}")
            else:
                print(f"{chave}: {valor}")

# -------------------------------
# 3. Execução
# -------------------------------
if __name__ == "__main__":
    arquivo = "./data/extratos/itau_extrato_012026.pdf"
    print(f"📄 Lendo arquivo: {arquivo}")
    try:
        transacoes = extrair_transacoes(arquivo)
        if not transacoes:
            print("❌ Nenhuma transação encontrada. Verifique o formato do PDF.")
        else:
            df, resumo = analisar_transacoes(transacoes)
            imprimir_resumo(resumo)
            exportar_csv(df)
            
            # Gráficos opcionais
            try:
                import matplotlib.pyplot as plt
                # Evolução do saldo (usando dados com saldo conhecido)
                df_saldo = df.dropna(subset=['saldo']).copy()
                if not df_saldo.empty:
                    plt.figure(figsize=(10,4))
                    plt.plot(df_saldo['data'], df_saldo['saldo'], marker='o', linestyle='-')
                    plt.title('Evolução do Saldo da Conta')
                    plt.xlabel('Data')
                    plt.ylabel('Saldo (R$)')
                    plt.grid(True)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.savefig('saldo_evolucao.png')
                    print("📈 Gráfico da evolução do saldo salvo como 'saldo_evolucao.png'")
                
                # Top despesas por categoria
                despesas_cat = df[df['valor'] < 0].groupby('categoria')['valor'].sum().abs().sort_values(ascending=False).head(5)
                if not despesas_cat.empty:
                    plt.figure(figsize=(8,4))
                    despesas_cat.plot(kind='bar', color='salmon')
                    plt.title('Maiores Despesas por Categoria')
                    plt.ylabel('Valor (R$)')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.savefig('despesas_categoria.png')
                    print("📊 Gráfico de despesas por categoria salvo como 'despesas_categoria.png'")
            except ImportError:
                print("⚠️ Matplotlib não instalado. Gráficos não gerados.")
    except FileNotFoundError:
        print(f"❌ Arquivo '{arquivo}' não encontrado.")
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")