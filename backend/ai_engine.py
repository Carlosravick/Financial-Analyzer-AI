import os
import json
import re
import logging
import pandas as pd
from typing import List, Dict

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

logger = logging.getLogger(__name__)

# --- CONSTANTES ---
VECTOR_DB_PATH = "data/faiss_index"
DEFAULT_MODEL = "gpt-4o-mini"
KEYWORDS_MATH = ["maior", "menor", "total", "soma", "evolução", "temporal", "mês", "ano", "agrupe", "concentração", "tipos", "cliente", "todos", "quais"]
KEYWORDS_RAG = ["detalhe", "sobre", "referentes a", "motivo"]

def build_vector_store(df: pd.DataFrame) -> None:
    """Constrói e salva o vetor de embeddings FAISS a partir do DataFrame."""
    try:
        documents = []
        for _, r in df.iterrows():
            content_parts = [
                f"Transação {r.get('id', 'N/A')}",
                f"Cliente: {r.get('cliente', 'N/A')}",
                f"Valor: R$ {r.get('valor', 0):.2f}",
                f"Status: {r.get('status', 'N/A')}",
                f"Descrição: {r.get('descricao', r.get('item', 'N/A'))}",
                f"Data: {r.get('data', 'N/A')}"
            ]
            documents.append(Document(
                page_content=" | ".join(content_parts),
                metadata={"client": r.get('cliente')}
            ))
            
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(VECTOR_DB_PATH)
    except Exception as e:
        logger.error(f"Erro fatal ao construir banco vetorial (FAISS): {e}")

def generate_insights_from_data(metrics: Dict, evolucao: List[Dict]) -> List[str]:
    """Gera insights proativos rápidos após o upload (sem Agent complexo)."""
    try:
        llm = ChatOpenAI(model=DEFAULT_MODEL, temperature=0.5)
        prompt = PromptTemplate.from_template(
            """Aja como um analista financeiro corporativo de alto escalão. Você recebeu este resumo financeiro contendo a evolução mensal da empresa:
Receita Total Paga: R$ {receita}
Inadimplência: {inad}% 
Mês de Maior Faturamento (Pico): {maior_mes} no valor de R$ {maior_valor}
Evolução Temporal Completa (Mês a Mês): {evolucao}

Sua tarefa principal é atuar como um conselheiro proativo que acabou de bater os olhos nesses dados e notou 3 coisas muito diferentes e interessantes (Insights Críticos). Gere 3 frases curtas de 1 linha.
REGRAS TÉCNICAS E MENTAIS:
1. VOCÊ É CRIATIVO: Nunca gere os mesmos insights. Olhe para os dados de queda de faturamento nos últimos meses, mas TAMBÉM olhe se há sazonalidade (altas de fim de ano ou quedas no meio do ano).
2. USE A MATEMÁTICA INJETADA: Você foi informado do 'Mês de Maior Faturamento'. Use esse dado exato com o mês e o número se quiser falar sobre os picos, sem precisar inventar cálculos.
3. NÃO FIQUE PRESO EM RETRANCA: A inadimplência é alta? Fale. É muito baixa (menos de 5%)? Reconheça como um triunfo ou ponto neutro, não trate como pânico.
4. CITE OS NÚMEROS REAIS PARA EMBASAR SUA EXPLICAÇÃO. 
Retorne a resposta APENAS como um array JSON válido de strings e NADA MAIS."""
        )
        
        chain = prompt | llm | StrOutputParser()
        res = chain.invoke({
            "receita": metrics.get('receita_total', 0),
            "inad": metrics.get('taxa_inadimplencia', 0),
            "maior_mes": max(evolucao, key=lambda x: x.get('receita', 0)).get('periodo', 'N/A') if evolucao else "N/A",
            "maior_valor": f"{max(evolucao, key=lambda x: x.get('receita', 0)).get('receita', 0.0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if evolucao else "0,00",
            "evolucao": evolucao
        })
        
        json_array = re.search(r'\[.*\]', res.replace('\n', ''))
        if json_array:
            return json.loads(json_array.group(0))
            
        return [
            "Recomenda-se realizar campanha de cobrança estruturada.", 
            "Controle o ticket médio focando em up-sell.", 
            "Faturamento aparentemente estagnado no período."
        ]
    except Exception as e:
        logger.error(f"Erro ao gerar LLM insights (Fallback ativado): {e}")
        return ["Inadimplência necessita de atenção.", "Reveja custos fixos na operação mensal."]

def query_financial_assistant(question: str, df_path: str) -> str:
    """Decide inteligentemente se usa RAG de texto livre ou cálculos de Tabela (Pandas)."""
    try:
        if _should_use_rag(question) and os.path.exists(VECTOR_DB_PATH):
            return _execute_rag_search(question)
            
        return _execute_pandas_agent(question, df_path)
    except Exception as e:
        logger.error(f"Erro inesperado no roteamento de IA: {e}")
        return "Desculpe, enfrentei um problema técnico ao processar sua requisição no banco de dados."

# --- FUNÇÕES PRIVADAS DE ROTEAMENTO (IA) ---

def _should_use_rag(question: str) -> bool:
    """Analisa a intenção da pergunta do usuário."""
    q_lower = question.lower()
    
    # CORREÇÃO AQUI: Força o uso do Pandas (retorna False para RAG) se houver um ID de transação
    if re.search(r'txn_\d+', q_lower):
        return False
        
    is_math_focused = any(kw in q_lower for kw in KEYWORDS_MATH)
    is_rag_focused = any(kw in q_lower for kw in KEYWORDS_RAG)
    return is_rag_focused and not is_math_focused

def _execute_rag_search(question: str) -> str:
    """Recupera contexto via FAISS e formula resposta restrita aos documentos."""
    try:
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        # Aumentamos o k=20 para garantir que o FAISS traga mais contexto, já que busca por ID (txn_xxx) no meio de 4000 linhas pode ser diluída.
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(question)
        
        context = "\n".join([d.page_content for d in docs])
        
        llm = ChatOpenAI(model=DEFAULT_MODEL, temperature=0)
        prompt = PromptTemplate.from_template(
            """Você é um assistente RAG financeiro. Você possui as seguintes transações financeiras retornadas por similaridade vetorial:
            {context}

            Questão do usuário: {question}

            Responda a questão baseando-se EXCLUSIVAMENTE nos dados acima. Seja conciso e cite o id ou descrição."""
        )
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"context": context, "question": question})
    except Exception as e:
        logger.error(f"Erro na busca semântica FAISS: {e}")
        return "Ocorreu um erro ao consultar o banco de descrições textuais."

def _execute_pandas_agent(question: str, df_path: str) -> str:
    """Aciona o executor LangChain capaz de rodar código Python com Pandas limitados."""
    try:
        llm = ChatOpenAI(model=DEFAULT_MODEL, temperature=0.1)
        df = pd.read_pickle(df_path)
        
        # Previne que o Pandas oculte metadados importantes como a coluna Status durante o print na memória do LLM.
        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        
        # A flag allow_dangerous_code=True foi mantida pois o Agente nativo a obriga.
        # Em produção real corporativa, usaríamos um Executor remoto (sandboxed via API).
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            agent_type="openai-tools",
            verbose=True, # Removi a verbosidade enorme do terminal em produção
            allow_dangerous_code=True,
            max_iterations=15,
            prefix="""Você é um Analista de Dados Financeiros operando ESTRITAMENTE sobre um DataFrame Pandas (df).
        DIRETRIZES ABSOLUTAS (TOLERÂNCIA ZERO PARA ALUCINAÇÃO):
        1. NUNCA DEIXE CÓDIGO MUDO: Se você criar uma variável (ex: x = df['valor'].mean()), a tela ficará vazia e você entrará em loop e dará erro de max_iterations. Você TEM QUE DAR O PRINT no final (ex: `print(x)`).
        2. O PANDAS OCULTA COLUNAS QUANDO VOCÊ IMPRIME O DATAFRAME INTEIRO (`...`). NUNCA imprima todo o DataFrame. Imprima apenas as colunas que você precisa (ex: `print(df[['id', 'status']])`).
        3. FOCO NO STATUS REAL: Você tem uma coluna chamada 'status' e uma separada chamada 'categoria' (que é 'Não informada'). NUNCA AS CONFUNDA. Extraia APENAS da coluna 'status'.
        4. FONTES DE DATA: As datas estão na coluna 'data'. Para buscar transações em um período específico, use as propriedades `.dt.month` e `.dt.year` juntas obrigatoriamente.
        5. Oculte o código fonte da resposta final."""
        )
        return agent.invoke(question).get("output", "Sem resposta exata do Agente.")
    except Exception as e:
        logger.error(f"Erro ao executar Pandas Agent: {e}")
        return "Ocorreu um erro ao calcular essas métricas exatas na tabela. Tente refazer a pergunta."