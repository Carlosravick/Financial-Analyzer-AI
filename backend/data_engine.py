import io
import csv
import logging
import pandas as pd
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

def parse_file_to_df(content: bytes, filename: str) -> pd.DataFrame:
    """
    Processa e limpa dados de Excel (.xlsx) e CSV garantindo estrutura correta.
    """
    if filename.endswith(".xlsx"):
        df = pd.read_excel(io.BytesIO(content))
        # Normalizar nomes de colunas do excel
        df.columns = [str(c).strip().lower() for c in df.columns]
    else:
        # Tratamento seguro para CSV problemáticos (com ';' ou ',')
        decoded = content.decode('utf-8', errors='replace').splitlines()
        
        # Testar delimitador pela primeira linha ou segunda
        delimiter = ';' if ';' in decoded[0] else ','
        reader = csv.reader(decoded, delimiter=delimiter)
        
        header = next(reader)
        if header and header[0].startswith('\ufeff'):
            header[0] = header[0].lstrip('\ufeff')
        header = [h.strip().lower() for h in header]
        
        rows = []
        for row in reader:
            if not row: continue
            if len(row) > len(header):
                row = row[:len(header)-1] + [" ".join(row[len(header)-1:])]
            rows.append(row)
        
        df = pd.DataFrame(rows, columns=header)
    
    # Tratamento genérico de colunas comuns
    if 'valor' in df.columns:
        # Se o dado for string, tentamos limpar a sujeira (ex: "R$ 4.388,29").
        # Se NÃO for string (ex: Excel já envia float 4388.29), ignoramos o `.str.` para não quebrar tudo e virar "438829"
        if df['valor'].dtype == object or df['valor'].dtype == str:
            df['valor'] = df['valor'].astype(str)\
                .str.replace('R$', '', regex=False)\
                .str.replace('.', '', regex=False)\
                .str.replace(',', '.', regex=False)\
                .str.strip()
        
        # Converte tudo de volta para pandas numbers ignorando o que for texto impossivel
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0.0)
        
    if 'status' in df.columns:
        df['status'] = df['status'].astype(str).str.strip().str.lower()
        
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        # Preencher nulos com data atual caso exista erro
        df['data'] = df['data'].fillna(pd.Timestamp.now())
    else:
        # Cria uma coluna de 'data' retroativa fake apenas para o exemplo/teste se faltar
        logger.warning("Coluna 'data' não encontrada. Gerando dados de teste.")
        df['data'] = pd.date_range(end=pd.Timestamp.now(), periods=len(df))

    if 'categoria' not in df.columns:
        # Apenas cria a coluna vazia para que o LLM não quebre caso tente agrupar depois, 
        # deixando a "Classificação Inteligente" a cargo do proprio RAG/LLM dinamicamente
        df['categoria'] = 'Não informada'
        
    return df

def get_metrics_and_evolution(df: pd.DataFrame) -> Tuple[Dict, List[Dict]]:
    """ Calcula os KPIs financeiros e o agrupamento temporal. """
    
    # Cria a coluna mes_ano ANTES de filtrar, para que os DataFrames filtrados a possuam
    if 'data' in df.columns:
        df['mes_ano'] = df['data'].dt.to_period('M').astype(str)
    else:
        df['mes_ano'] = "Desconhecido"

    pago_df = df[df['status'] == 'pago']
    # Versão Sênior: Agrupa 'pendente' e 'atrasado' como risco/inadimplência (tudo que não entrou no caixa)
    inadimplencia_df = df[df['status'] != 'pago']
    
    valor_total = df['valor'].sum()
    inadimplencia_valor = inadimplencia_df['valor'].sum()
    
    metrics = {
        "receita_total": float(pago_df['valor'].sum()) if not pago_df.empty else 0.0,
        "ticket_medio": float(pago_df['valor'].mean()) if not pago_df.empty else 0.0,
        "taxa_inadimplencia": float((inadimplencia_valor / valor_total) * 100) if valor_total > 0 else 0.0,
        "total_transacoes": int(len(df))
    }
    
    # Evolução temporal por mês/ano (Faturamento)
    if not pago_df.empty:
        evolucao = pago_df.groupby('mes_ano')['valor'].sum().reset_index()
        evolucao.rename(columns={'mes_ano': 'periodo', 'valor': 'receita'}, inplace=True)
        evolucao_list = evolucao.to_dict('records')
    else:
        evolucao_list = []
    
    return metrics, evolucao_list
