import pdfplumber
import pandas as pd
import re
import os
from pathlib import Path

try:
    from data.holerites.gabriella.gabriella_privado import obter_dataframe_gabriella
    GABRIELLA_DISPONIVEL = True
except ImportError:
    print("⚠️ Arquivo gabriella_privado.py não encontrado. Criando DataFrame vazio para Gabriella.")
    GABRIELLA_DISPONIVEL = False
    def obter_dataframe_gabriella():
        return pd.DataFrame()

def extrair_referencia_do_nome_arquivo(nome_arquivo):
    match = re.search(r'(\d{2})-(\d{4})', nome_arquivo)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return None

def extrair_info_holerite_matheus(caminho_pdf):
    """Extrai dados do holerite do Matheus (Santander) - texto nativo."""
    texto_completo = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                texto_completo += texto + "\n"
    texto_plano = texto_completo.replace('\n', ' ')
    
    info = {
        'pessoa': 'matheus',
        'arquivo': os.path.basename(caminho_pdf),
        'caminho': str(caminho_pdf),
        'nome': None,
        'referencia': None,
        'data_pagamento': None,
        'salario_base': None,
        'total_liquido': None,
        'inss': None,
        'irrf': None,
    }
    
    # Nome
    match = re.search(r'Nome:\s*([A-Z\s]+?)(?:\d|$)', texto_plano, re.IGNORECASE)
    if match:
        info['nome'] = match.group(1).strip()
    else:
        match = re.search(r'CPF:([A-Za-zÀ-ÿ\s]+?)(\d{3}\.\d{3}\.\d{3}-\d{2})', texto_plano)
        if match:
            info['nome'] = match.group(1).strip()
    
    # Referência (prioriza nome do arquivo)
    info['referencia'] = extrair_referencia_do_nome_arquivo(info['arquivo'])
    
    # Data pagamento
    match = re.search(r'Dt\.\s*pagt\.:\s*(\d{2}/\d{2}/\d{4})', texto_plano)
    if match:
        info['data_pagamento'] = match.group(1)
    
    # Salário base
    match = re.search(r'Salário contratual:\s*([\d\.]+,\d{2})', texto_plano)
    if match:
        val = match.group(1).replace('.', '').replace(',', '.')
        info['salario_base'] = float(val)
    
    # Total líquido
    match = re.search(r'Total\s+líquido:\s*([\d\.]+,\d{2})', texto_plano)
    if not match:
        match = re.search(r'Total líquido:\s*([\d\.]+,\d{2})', texto_plano)
    if match:
        val = match.group(1).replace('.', '').replace(',', '.')
        info['total_liquido'] = float(val)
    
    # INSS
    match = re.search(r'INSS\s+[\d.]*,\d{2}\s+([\d\.]+,\d{2})', texto_plano)
    if not match:
        match = re.search(r'INSS\s+([\d\.]+,\d{2})', texto_plano)
    if match:
        val = match.group(1).replace('.', '').replace(',', '.')
        info['inss'] = float(val)
    
    # IRRF
    match = re.search(r'IRRF\s+[\d.]*,\d{2}\s+([\d\.]+,\d{2})', texto_plano)
    if not match:
        match = re.search(r'IRRF\s+([\d\.]+,\d{2})', texto_plano)
    if match:
        val = match.group(1).replace('.', '').replace(',', '.')
        info['irrf'] = float(val)
    
    return info

def processar_matheus(pasta_matheus):
    dados = []
    pdfs = list(Path(pasta_matheus).glob("**/*.pdf"))
    if not pdfs:
        print("⚠️ Nenhum PDF encontrado para Matheus.")
        return pd.DataFrame()
    for pdf_path in pdfs:
        print(f"📄 Processando Matheus: {pdf_path.name}")
        try:
            info = extrair_info_holerite_matheus(pdf_path)
            if info['total_liquido'] is not None:
                dados.append(info)
            else:
                print(f"   ⚠️ Total líquido não encontrado em {pdf_path.name}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    return pd.DataFrame(dados)

def salvar_excel_com_abas(df_matheus, df_gabriella, arquivo_saida):
    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
        # Aba 1: Matheus (detalhado)
        if not df_matheus.empty:
            df_matheus.to_excel(writer, sheet_name='Matheus', index=False)
        else:
            pd.DataFrame({'Aviso': ['Nenhum dado do Matheus']}).to_excel(writer, sheet_name='Matheus', index=False)
        
        # Aba 2: Gabriella (valores fixos)
        if not df_gabriella.empty:
            df_gabriella.to_excel(writer, sheet_name='Gabriella', index=False)
        else:
            pd.DataFrame({'Aviso': ['Nenhum dado da Gabriella']}).to_excel(writer, sheet_name='Gabriella', index=False)
        
        # Aba 3: Consolidado (junção das duas pessoas)
        df_consolidado = pd.concat([df_matheus, df_gabriella], ignore_index=True)
        if not df_consolidado.empty:
            # Remove colunas totalmente nulas
            df_consolidado = df_consolidado.dropna(axis=1, how='all')
            df_consolidado.to_excel(writer, sheet_name='Consolidado', index=False)
            
            # Aba 4: Pivot mensal (valores por pessoa e mês)
            pivot = df_consolidado.pivot_table(index='referencia', columns='pessoa', values='total_liquido', aggfunc='sum')
            pivot.to_excel(writer, sheet_name='Pivot_mensal')
    
    print(f"✅ Relatório salvo em {arquivo_saida}")

# -------------------------------
# EXECUÇÃO PRINCIPAL
# -------------------------------
if __name__ == "__main__":
    PASTA_MATHEUS = "./data/holerites/matheus/"
    ARQUIVO_SAIDA = "./data/relatorio_holerites.xlsx"
    
    # Processa Matheus
    df_matheus = processar_matheus(PASTA_MATHEUS)
    
    # Obtém DataFrame da Gabriella (do arquivo privado)
    df_gabriella = obter_dataframe_gabriella() if GABRIELLA_DISPONIVEL else pd.DataFrame()
    
    # Exibe resumo rápido no console
    print("\n" + "="*70)
    print("📊 RESUMO CONSOLIDADO (CONSOLE)")
    print("="*70)
    if not df_matheus.empty:
        total_matheus = df_matheus['total_liquido'].sum()
        print(f"Matheus: {len(df_matheus)} holerite(s) - Total R$ {total_matheus:,.2f}")
    else:
        print("Matheus: nenhum dado")
    
    if not df_gabriella.empty:
        total_gabriella = df_gabriella['total_liquido'].sum()
        print(f"Gabriella: {len(df_gabriella)} holerite(s) - Total R$ {total_gabriella:,.2f}")
    else:
        print("Gabriella: nenhum dado (verifique o arquivo gabriella_privado.py)")
    
    if not df_matheus.empty or not df_gabriella.empty:
        total_geral = (df_matheus['total_liquido'].sum() if not df_matheus.empty else 0) + \
                      (df_gabriella['total_liquido'].sum() if not df_gabriella.empty else 0)
        print(f"\n💰 Total geral líquido: R$ {total_geral:,.2f}")
    
    # Salva Excel com abas separadas
    salvar_excel_com_abas(df_matheus, df_gabriella, ARQUIVO_SAIDA)


# ========================
# ======= ANÁLISES =======
# ========================

from config.config import SHEET_NAME
df = pd.read_excel(ARQUIVO_SAIDA, sheet_name=SHEET_NAME)

df = df[['pessoa', 'referencia', 'total_liquido']]
print(df)