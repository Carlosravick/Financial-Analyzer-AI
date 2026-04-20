import io
import csv
import logging
import pandas as pd
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# --- CONSTANTES ---
COL_VALOR = 'valor'
COL_STATUS = 'status'
COL_DATA = 'data'
COL_CATEGORIA = 'categoria'
STATUS_PAGO = 'pago'

def parse_file_to_df(content: bytes, filename: str) -> pd.DataFrame:
    """Função orquestradora: Carrega os dados e orquestra a limpeza."""
    df = _load_dataframe(content, filename)
    return _clean_dataframe_columns(df)

# --- FUNÇÕES PRIVADAS DE CARREGAMENTO ---
def _load_dataframe(content: bytes, filename: str) -> pd.DataFrame:
    if filename.endswith(".xlsx"):
        return _parse_excel(content)
    return _parse_csv(content)

def _parse_excel(content: bytes) -> pd.DataFrame:
    try:
        df = pd.read_excel(io.BytesIO(content))
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        logger.error(f"Erro ao ler Excel: {e}")
        raise ValueError(f"Falha ao processar o arquivo Excel. Verifique se o arquivo está corrompido.")

def _parse_csv(content: bytes) -> pd.DataFrame:
    try:
        decoded = content.decode('utf-8', errors='replace').splitlines()
        if not decoded:
            raise ValueError("O arquivo CSV está vazio.")
            
        delimiter = ';' if ';' in decoded[0] else ','
        reader = csv.reader(decoded, delimiter=delimiter)
        
        header = next(reader, None)
        if not header:
            raise ValueError("Cabeçalho não encontrado no arquivo CSV.")
            
        if header and header[0].startswith('\ufeff'):
            header[0] = header[0].lstrip('\ufeff')
        header = [h.strip().lower() for h in header]
        
        rows = []
        for row in reader:
            if not row: continue
            if len(row) > len(header):
                row = row[:len(header)-1] + [" ".join(row[len(header)-1:])]
            rows.append(row)
        
        return pd.DataFrame(rows, columns=header)
    except Exception as e:
        logger.error(f"Erro ao ler CSV: {e}")
        raise ValueError(f"Falha ao processar o arquivo CSV. Verifique a formatação do arquivo.")

# --- FUNÇÕES PRIVADAS DE LIMPEZA (SANITIZAÇÃO) ---
def _clean_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica regras de negócio e formatação de acordo com a coluna."""
    if COL_VALOR in df.columns:
        df[COL_VALOR] = _clean_currency_column(df[COL_VALOR])
        
    if COL_STATUS in df.columns:
        df[COL_STATUS] = df[COL_STATUS].astype(str).str.strip().str.lower()
        
    if COL_DATA in df.columns:
        df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors='coerce').fillna(pd.Timestamp.now())
    else:
        logger.warning(f"Coluna '{COL_DATA}' não encontrada. Gerando dados de teste.")
        df[COL_DATA] = pd.date_range(end=pd.Timestamp.now(), periods=len(df))

    if COL_CATEGORIA not in df.columns:
        df[COL_CATEGORIA] = 'Não informada'
        
    return df

def _clean_currency_column(series: pd.Series) -> pd.Series:
    """Remove caracteres monetários e converte a série para float exato."""
    if series.dtype == object or series.dtype == str:
        cleaned = series.astype(str)\
            .str.replace('R$', '', regex=False)\
            .str.replace('.', '', regex=False)\
            .str.replace(',', '.', regex=False)\
            .str.strip()
        return pd.to_numeric(cleaned, errors='coerce').fillna(0.0)
    return pd.to_numeric(series, errors='coerce').fillna(0.0)

def get_metrics_and_evolution(df: pd.DataFrame) -> Tuple[Dict, List[Dict]]:
    """ Calcula os KPIs financeiros e o agrupamento temporal. """
    
    # Cria uma cópia para evitar mutações no DataFrame original durante o cálculo dos KPIs
    df_work = df.copy()
    
    if COL_DATA in df_work.columns:
        df_work['mes_ano'] = df_work[COL_DATA].dt.to_period('M').astype(str)
    else:
        df_work['mes_ano'] = "Desconhecido"

    pago_df = df_work[df_work[COL_STATUS] == STATUS_PAGO]
    inadimplencia_df = df_work[df_work[COL_STATUS] != STATUS_PAGO]
    
    valor_total = df_work[COL_VALOR].sum()
    inadimplencia_valor = inadimplencia_df[COL_VALOR].sum()
    
    metrics = {
        "receita_total": float(pago_df[COL_VALOR].sum()) if not pago_df.empty else 0.0,
        "ticket_medio": float(pago_df[COL_VALOR].mean()) if not pago_df.empty else 0.0,
        "taxa_inadimplencia": float((inadimplencia_valor / valor_total) * 100) if valor_total > 0 else 0.0,
        "total_transacoes": int(len(df_work))
    }
    
    if not pago_df.empty:
        evolucao = pago_df.groupby('mes_ano')[COL_VALOR].sum().reset_index()
        evolucao.rename(columns={'mes_ano': 'periodo', COL_VALOR: 'receita'}, inplace=True)
        evolucao_list = evolucao.to_dict('records')
    else:
        evolucao_list = []
    
    return metrics, evolucao_list
