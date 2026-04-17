import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import QuestionRequest, UploadResponse, AskResponse
from data_engine import parse_file_to_df, get_metrics_and_evolution
from ai_engine import build_vector_store, generate_insights_from_data, query_financial_assistant

# Configuração Padrão
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Plataforma de Inteligência Financeira", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_CACHE_PATH = "data/processed_data.pkl"
os.makedirs("data", exist_ok=True)

@app.post("/upload", response_model=UploadResponse)
async def upload_financial_data(file: UploadFile = File(...)):
    """
    Ingestão Multilíngue (CSV/XLSX), Limpeza e Preparação para RAG/Pandas.
    """
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        raise HTTPException(status_code=400, detail="Formato inválido. Use CSV ou XLSX.")

    try:
        content = await file.read()
        
        # 1. Pipeline de Ingestão Genérica e Robusta
        df = parse_file_to_df(content, file.filename)
        
        # Cache estruturado
        df.to_pickle(DATA_CACHE_PATH)
        
        # 2. Métricas Baseadas em DataFrame Limpo
        metrics, evolucao = get_metrics_and_evolution(df)
        
        # 3. Insights Proativos com LLM usando o Sumário
        insights = generate_insights_from_data(metrics, evolucao)

        # 4. RAG Vectorization: Background task ou Block (aqui Bloqueante MVP)
        build_vector_store(df)
        logger.info("Upload Completo: RAG, Dados e Modelos atualizados.")

        # Retornar dados ao Frontend
        return UploadResponse(
            message="Processado com excelência",
            metrics={**metrics, "evolucao_temporal": evolucao},
            insights=insights
        )

    except Exception as e:
        logger.error(f"Upload Flow falhou: {e}")
        raise HTTPException(status_code=500, detail="Erro Crítico de Processamento.")

@app.post("/ask", response_model=AskResponse)
async def ask_question(req: QuestionRequest):
    """
    Roteador Inteligente de Consultas RAG x Relacionais (Pandas).
    """
    if not os.path.exists(DATA_CACHE_PATH):
        raise HTTPException(status_code=400, detail="Cache vazio. Execute Upload antes.")

    try:
        # A Mágica de Escolha RAG x Pandas acontece aqui
        answer = query_financial_assistant(req.question, DATA_CACHE_PATH)
        return AskResponse(question=req.question, answer=answer)

    except Exception as e:
        logger.error(f"Consulta Falhou: {e}")
        raise HTTPException(status_code=500, detail="Erro de Inteligência Artificial.")
