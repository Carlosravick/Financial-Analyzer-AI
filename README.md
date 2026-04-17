# Case: Plataforma de Inteligência Financeira com IA

## Visão Geral e Arquitetura

O **Financial Analyzer AI** foi desenvolvido utilizando os conceitos de **Clean Architecture** (Separação de Responsabilidades), e conta com as seguintes ferramentas:
- **Backend:** Python + FastAPI, encapsulando a lógica de Ingestão de Dados (Pandas), e Inteligência Artificial.
- **Frontend:** Next.js + React.js, provendo uma interface limpa com renderização de gráficos, análise preditiva e Chat RAG.
- **IA Stack:** Diferenciei a aplicação implementando um sistema com Roteamento Inteligente (*Smart Router*). Diferente de usar apenas um Agente, a API envia a pergunta do usuário para o **FAISS (Vetor semântico Embeddings de Busca RAG)**, caso ele precise de descrições e itens contábeis, ou usa um engine **Pandas DataFrame Agent** da OpenAI (Functions), se forem cálculos e consolidações exatas, evitando alucinações nas contas de agregação.

## Decisões Técnicas

1. **Uso do Modelo `gpt-4o-mini`:** Focado na eficiência técnica e de custos (Tokens). Ele é incrivelmente rápido e extremamente eficiente em seguir as guidelines rigorosas passadas pelo "System Prompt" no Pandas Agent, enquanto nos poupa dinheiro nos requests repetitivos de Embeddings.
2. **Separação de Rotas Modulares:** Criei os arquivos (`data_engine.py`, `ai_engine.py`, `models.py`) em pró da testabilidade e manutenibilidade contínua que uma equipe Sênior precisa, e não deixar tudo acoplado dentro do Endpoint/main.
3. **Parsing de Excel / CSV Complexo:** O Worker no serviço de Data Engine extrai BOMs (\ufeff), lida com planilhas que estouram delimitadores (CSV ';' vs ',') e padroniza a formatação contábil para Float exato antes mesmo do LLM encostar nela.
4. **Insights Proativos (Automáticos):** Ao fazer o Upload, o backend executa _zero-shot processing_ onde analisa a situação macro da empresa com base no resumo processado, exibindo dicas ativas no front (ex: controle de inadimplência), em vez de apenas agendar o RAG ou depender do chat.

## Funcionalidades Solicitadas:
- ✅ *Processar dados financeiros e gerar Upload:* Agora lida com CSV e XLSX nativamente.
- ✅ *Métricas e Insights automáticos:* Dashboard reativo gerando receita, ticket, inadimplência + Dicas de IA e Gráfico Temporal (`recharts`).
- ✅ *RAG Respostas com Embeddings (FAISS):* Ao utilizar as "keywords" de busca no chat ("Quais itens", "detalhe", etc).
- ✅ *Docker-compose e deploy:* Tudo pronto pra provisionamento em instâncias locais.

## Instruções de Instalação e Uso

### Utilizando Docker
1. Crie o arquivo `.env` no subdiretório `backend` (exemplo: `backend/.env`) com a chave da OpenAI:
   `OPENAI_API_KEY=sk-...` (Sua chave)
2. Retorne a raíz do repositório (onde o arquivo `docker-compose.yml` está).
3. Execute o comando:
   ```bash
   docker-compose up --build
   ```
4. Navegue até o frontend em: [http://localhost:3000](http://localhost:3000)

### Instalação e Execução Manual
**Backend (FastAPI)**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate # Em linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Next.js)**
```bash
cd frontend
npm install
npm run dev
```

*Frontend estará ativo na porta 3000.*

---
Espero que gostem da aplicação! Caso precise gravar o vídeo explicativo de 5 minutos, foque primeiramente na arquitetura (como dividimos Pandas vs Embeddings RAG) e na UX fluída dos cards na UI.
