import os
import json
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

VECTOR_DB_PATH = "data/faiss_index"

def build_vector_store(df: pd.DataFrame):
    """Constrói e salva o vetor de embeddings FAISS."""
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

def generate_insights_from_data(metrics: Dict, evolucao: List[Dict]) -> List[str]:
    """Gera insights proativos rápidos após o upload (sem Agent complexo)."""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        prompt = PromptTemplate.from_template(
            "Aja como um analista financeiro sênior. Você recebeu este resumo financeiro:\n"
            "Receita Total: {receita}\n"
            "Inadimplência: {inad}% \n"
            "Evolução Temporal: {evolucao}\n\n"
            "Gere exatamente 3 insights importantes, curtos (1 frase) e acionáveis sobre esses dados."
            "Retorne a resposta como um array JSON válido."
        )
        
        chain = prompt | llm | StrOutputParser()
        res = chain.invoke({
            "receita": metrics['receita_total'],
            "inad": metrics['taxa_inadimplencia'],
            "evolucao": evolucao
        })
        
        import re
        json_array = re.search(r'\[.*\]', res.replace('\n', ''))
        if json_array:
            return json.loads(json_array.group(0))
        return ["Recomenda-se realizar campanha de cobrança estruturada.", 
                "Controle o ticket médio focando em up-sell.", 
                "Faturamento aparentemente estável no período."]
    except Exception as e:
        logger.error(f"Erro em generate_insights: {e}")
        return ["Inadimplência necessita de atenção.", "Reveja custos fixos."]

def query_financial_assistant(question: str, df_path: str) -> str:
    """Decide inteligentemente se usa RAG de texto livre ou cálculos de Tabela (Pandas)."""
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # 1. Roteamento: É uma pergunta de "Lista/Descricao" ou "Matematica/Matriz"?
    # Vamos usar regras mais precisas para não enviar contas complexas pro RAG (Vetor)
    question_lower = question.lower()
    
    keywords_math = ["maior", "menor", "total", "soma", "evolução", "temporal", "mês", "ano", "agrupe", "concentração"]
    is_math_focused = any(kw in question_lower for kw in keywords_math)
    
    keywords_rag = ["detalhe", "sobre", "referentes a", "motivo"]
    is_rag_focused = any(kw in question_lower for kw in keywords_rag) and not is_math_focused
    
    if is_rag_focused and os.path.exists(VECTOR_DB_PATH):
        # USA RAG (FAISS) 
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(question)
        
        context = "\n".join([d.page_content for d in docs])
        
        prompt = PromptTemplate.from_template(
            "Você é um assistente RAG financeiro. Você possui as seguintes transações financeiras retornadas por similaridade vetorial:\n"
            "{context}\n\n"
            "Questão do usuário: {question}\n\n"
            "Responda a questão baseando-se EXCLUSIVAMENTE nos dados acima. Seja conciso e cite o id ou descrição."
        )
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"context": context, "question": question})
    
    else:
        # USA PANDAS AGENT
        df = pd.read_pickle(df_path)
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            agent_type="openai-tools",
            verbose=True,
            allow_dangerous_code=True,
            prefix=(
                "Você é um Analista de Dados Sênior.\n"
                "REGRAS CRÍTICAS E ABSOLUTAS (ZERO ALUCINAÇÃO):\n"
                "1. NUNCA INVENTE NÚMEROS MENTALMENTE. Todo e qualquer valor (seja total, valor intermediário, semestre ou diferença) DEVE vir exclusivamente do output da execução do seu código Pandas.\n"
                "2. Se a pergunta comparar duas variáveis (ex: Semestre 1 e Semestre 2), o seu código Python DEVE obrigatoriamente fazer o `print()` dos dois valores isolados e da diferença exata para você poder ler antes de ditar a resposta final.\n"
                "3. Considere SEMPRE que qualquer status DIVERENTE de 'pago' (como 'pendente' ou 'atrasado') representa a INADIMPLÊNCIA do negócio.\n"
                "4. Formate a saída financeira como R$ 0.000,00.\n"
                "5. Forneça insights concisos, baseando-se restritamente na exatidão matemática do Python."
            )
        )
        return agent.invoke(question)["output"]
