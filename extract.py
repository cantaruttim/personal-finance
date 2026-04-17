import pdfplumber
import pandas as pd
import re
from datetime import datetime
from collections import Counter
import os

# --------------------------
# Função para salvar imagens
# --------------------------
def salvar_imagem(fig, nome_arquivo, caminho="./util/graficos/", dpi=300, bbox_inches='tight'):
    os.makedirs(caminho, exist_ok=True)
    caminho_completo = os.path.join(caminho, nome_arquivo)
    print(f"Salvando imagem: {caminho_completo}")
    fig.savefig(caminho_completo, dpi=dpi, bbox_inches=bbox_inches)
    print("✅ Imagem salva com sucesso!")

# -------------------------------
# Função para salvar múltiplas abas em Excel
# -------------------------------
def salva_multiplas_abas(abas_dict, file_path_output, file_name):
    """
    Salva múltiplos DataFrames em um único arquivo Excel, cada um em uma aba.
    
    Args:
        abas_dict: dicionário no formato {nome_da_aba: dataframe}
        file_path_output: caminho da pasta onde salvar (ex: "./output/")
        file_name: nome do arquivo (sem extensão)
    """
    # Garante que o diretório existe
    os.makedirs(file_path_output, exist_ok=True)
    caminho_completo = os.path.join(file_path_output, f"{file_name}.xlsx")
    print(f"📁 Salvando arquivo com {len(abas_dict)} abas em {caminho_completo}...")
    
    try:
        with pd.ExcelWriter(caminho_completo, engine='openpyxl') as writer:
            for nome_aba, df in abas_dict.items():
                print(f"  -> Criando aba '{nome_aba}' com {len(df)} linhas")
                df.to_excel(writer, sheet_name=nome_aba, index=False)
        print(f"✅ Arquivo Excel salvo com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")

# -------------------------------
# 1. Extrair transações do PDF
# -------------------------------
def extrair_transacoes(caminho_pdf):
    transacoes = []
    saldo_por_data = {}
    lancamentos_por_data = {}

    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            linhas = text.split('\n')
            for linha in linhas:
                match = re.match(r'(\d{2}/\d{2}/\d{4})\s+(.+)', linha.strip())
                if not match:
                    continue
                data_str, resto = match.groups()
                data = datetime.strptime(data_str, '%d/%m/%Y')
                
                valor_match = re.search(r'(-?\d{1,3}(?:\.\d{3})*,\d{2})\s*$', resto)
                if not valor_match:
                    continue
                
                valor_str = valor_match.group(1)
                valor_str = valor_str.replace('.', '').replace(',', '.')
                valor = float(valor_str)
                descricao = resto[:valor_match.start()].strip()
                
                if descricao.upper() == "SALDO DO DIA":
                    saldo_por_data[data] = valor
                else:
                    descricao_limpa = re.sub(r'\d{2}/\d{4}', '', descricao).strip()
                    lancamentos_por_data.setdefault(data, []).append((descricao_limpa, valor))
    
    for data, lancamentos in lancamentos_por_data.items():
        saldo = saldo_por_data.get(data, None)
        for desc, val in lancamentos:
            transacoes.append({
                'data': data,
                'descricao': desc,
                'valor': val,
                'saldo': saldo
            })
    transacoes.sort(key=lambda x: x['data'])
    return transacoes

# -------------------------------
# 2. Categorização
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

# -------------------------------
# 3. Análise e geração dos DataFrames para o Excel
# -------------------------------
def analisar_e_preparar_abas(transacoes):
    df = pd.DataFrame(transacoes)
    if df.empty:
        return None, {}
    
    df['tipo'] = df['valor'].apply(lambda x: 'Crédito' if x > 0 else 'Débito')
    df['categoria'] = df['descricao'].apply(categorizar_descricao)
    
    # Aba 1: transações detalhadas
    df_transacoes = df.copy()
    df_transacoes['data'] = df_transacoes['data'].dt.strftime('%d/%m/%Y')
    df_transacoes['valor'] = df_transacoes['valor'].apply(lambda x: f"{x:.2f}")
    df_transacoes['saldo'] = df_transacoes['saldo'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    
    # Aba 2: resumo
    total_credito = df[df['valor'] > 0]['valor'].sum()
    total_debito = df[df['valor'] < 0]['valor'].sum()
    num_transacoes = len(df)
    df_com_saldo = df.dropna(subset=['saldo'])
    if not df_com_saldo.empty:
        saldo_inicial = df_com_saldo.iloc[0]['saldo'] - df_com_saldo.iloc[0]['valor']
        saldo_final = df_com_saldo.iloc[-1]['saldo']
    else:
        saldo_inicial = saldo_final = None
    
    resumo_dict = {
        'Indicador': ['Período', 'Saldo inicial', 'Saldo final', 'Total créditos', 'Total débitos', 
                      'Variação líquida', 'Número de transações', 'Maior crédito', 'Maior débito'],
        'Valor': [
            f"{df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}",
            f"R$ {saldo_inicial:.2f}" if saldo_inicial else 'N/A',
            f"R$ {saldo_final:.2f}" if saldo_final else 'N/A',
            f"R$ {total_credito:.2f}",
            f"R$ {abs(total_debito):.2f}",
            f"R$ {total_credito + total_debito:.2f}",
            num_transacoes,
            f"R$ {df['valor'].max():.2f}",
            f"R$ {df['valor'].min():.2f}"
        ]
    }
    df_resumo = pd.DataFrame(resumo_dict)
    
    # Aba 3: créditos por categoria
    cat_credito = df[df['valor'] > 0].groupby('categoria')['valor'].sum().reset_index()
    cat_credito.columns = ['Categoria', 'Valor Total (R$)']
    cat_credito = cat_credito.sort_values('Valor Total (R$)', ascending=False)
    
    # Aba 4: débitos por categoria
    cat_debito = df[df['valor'] < 0].groupby('categoria')['valor'].sum().abs().reset_index()
    cat_debito.columns = ['Categoria', 'Valor Total (R$)']
    cat_debito = cat_debito.sort_values('Valor Total (R$)', ascending=False)
    
    # Aba 5: top contrapartes (PIX/TED)
    contrapartes = []
    for _, row in df.iterrows():
        desc = row['descricao'].upper()
        if 'PIX TRANSF' in desc or 'TED' in desc:
            resto = re.sub(r'(PIX TRANSF|TED)', '', desc).strip()
            if resto:
                contrapartes.append(resto)
    contagem = Counter(contrapartes).most_common(10)
    df_contrapartes = pd.DataFrame(contagem, columns=['Contraparte', 'Número de Transações'])
    
    # Monta dicionário de abas
    abas = {
        'transacoes': df_transacoes,
        'resumo_financeiro': df_resumo,
        'creditos_por_categoria': cat_credito,
        'debitos_por_categoria': cat_debito,
        'top_contrapartes': df_contrapartes
    }
    return df, abas

# -------------------------------
# 4. Execução principal
# -------------------------------
FILE_NAME = "./data/extratos/itau_extrato_012026.pdf"
OUTPUT_EXCEL_PATH = "./data/"
OUTPUT_EXCEL_NAME = "analise_extrato_itau"

if __name__ == "__main__":
    print(f"📄 Lendo arquivo: {FILE_NAME}")
    try:
        transacoes = extrair_transacoes(FILE_NAME)
        if not transacoes:
            print("❌ Nenhuma transação encontrada.")
        else:
            df, abas = analisar_e_preparar_abas(transacoes)
            
            # Salva Excel com múltiplas abas
            salva_multiplas_abas(abas, OUTPUT_EXCEL_PATH, OUTPUT_EXCEL_NAME)
            
            # Geração de gráficos (opcional, usando a função salvar_imagem)
            try:
                import matplotlib.pyplot as plt
                
                # Evolução do saldo
                df_saldo = df.dropna(subset=['saldo']).copy()
                if not df_saldo.empty:
                    fig1, ax1 = plt.subplots(figsize=(10, 4))
                    ax1.plot(df_saldo['data'], df_saldo['saldo'], marker='o', linestyle='-')
                    ax1.set_title('Evolução do Saldo da Conta')
                    ax1.set_xlabel('Data')
                    ax1.set_ylabel('Saldo (R$)')
                    ax1.grid(True)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    salvar_imagem(fig1, 'saldo_evolucao.png')
                    plt.close(fig1)
                
                # Top despesas por categoria
                despesas_cat = df[df['valor'] < 0].groupby('categoria')['valor'].sum().abs().sort_values(ascending=False).head(5)
                if not despesas_cat.empty:
                    fig2, ax2 = plt.subplots(figsize=(8, 4))
                    despesas_cat.plot(kind='bar', color='salmon', ax=ax2)
                    ax2.set_title('Maiores Despesas por Categoria')
                    ax2.set_ylabel('Valor (R$)')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    salvar_imagem(fig2, 'despesas_categoria.png')
                    plt.close(fig2)
                
                print("📊 Gráficos salvos em './util/graficos/'")
            except ImportError:
                print("⚠️ Matplotlib não instalado. Gráficos não gerados.")
    except FileNotFoundError:
        print(f"❌ Arquivo '{FILE_NAME}' não encontrado.")
    except Exception as e:
        print(f"❌ Erro: {e}")