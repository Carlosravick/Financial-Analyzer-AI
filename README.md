# Case: Plataforma de Inteligência Financeira com IA

## 🎥 Apresentação do Projeto
Confira o vídeo de apresentação e explicação técnica do projeto no YouTube: 
[![Demonstração do Projeto](https://img.youtube.com/vi/MfuscmHL1eA/0.jpg)](https://youtu.be/MfuscmHL1eA)

🔗 **Link direto para o vídeo:** [https://youtu.be/MfuscmHL1eA](https://youtu.be/MfuscmHL1eA)

## Visão Geral e Arquitetura

O **Financial Analyzer AI** foi desenvolvido utilizando os conceitos de **Clean Architecture** (Separação de Responsabilidades), e conta com as seguintes ferramentas:
- **Backend:** Python + FastAPI, encapsulando a lógica de Ingestão de Dados (Pandas), e Inteligência Artificial.
- **Frontend:** Next.js + React.js, provendo uma interface limpa com renderização de gráficos, análise preditiva e Chat RAG. O código segue os princípios de **Clean Code**, sendo fortemente tipado com TypeScript, utilizando separação de componentes lógicos (`src/components`), isolamento da camada de serviços de API (`src/services`), e variáveis de ambiente configuráveis (`.env.local`).
- **IA Stack:** Diferenciei a aplicação implementando um sistema com Roteamento Inteligente (*Smart Router*). Diferente de usar apenas um Agente, a API envia a pergunta do usuário para o **FAISS (Vetor semântico Embeddings de Busca RAG)**, caso ele precise de descrições e itens contábeis, ou usa um engine **Pandas DataFrame Agent** da OpenAI (Functions), se forem cálculos e consolidações exatas, evitando alucinações nas contas de agregação.

## Decisões Técnicas

1. **Uso do Modelo `gpt-4o-mini`:** Focado na eficiência técnica e de custos (Tokens). Ele é incrivelmente rápido e extremamente eficiente em seguir as guidelines rigorosas passadas pelo "System Prompt" no Pandas Agent, enquanto nos poupa dinheiro nos requests repetitivos de Embeddings.
2. **Separação de Rotas Modulares:** O backend foi estruturado em módulos independentes (`data_engine.py`, `ai_engine.py`, `models.py`) para facilitar a manutenção, clareza e evolução do código, evitando que lógicas complexas fiquem todas agrupadas no arquivo principal.
3. **Parsing de Excel / CSV Complexo:** O Worker no serviço de Data Engine extrai BOMs (\ufeff), lida com planilhas que estouram delimitadores (CSV ';' vs ',') e padroniza a formatação contábil para Float exato antes mesmo do LLM encostar nela.
4. **Insights Proativos (Automáticos):** Ao fazer o Upload, o backend executa _zero-shot processing_ onde analisa a situação macro da empresa com base no resumo processado, exibindo dicas ativas no front (ex: controle de inadimplência), em vez de apenas agendar o RAG ou depender do chat.
5. **Clean Code no Frontend:** O Frontend em Next.js foi estruturado isolando responsabilidades, removendo acoplamento forte entre UI e regras de chamadas de API (isoladas em `src/services/api.ts`). Todo o projeto é estritamente tipado (Interfaces TypeScript em `src/types`), garantindo estabilidade e escalabilidade, e centralizando credenciais (com o uso de `.env.local`).

## Funcionalidades Solicitadas:
- ✅ *Processar dados financeiros e gerar Upload:* Agora lida com CSV e XLSX nativamente.
- ✅ *Métricas e Insights automáticos:* Dashboard reativo gerando receita, ticket, inadimplência + Dicas de IA e Gráfico Temporal (`recharts`).
- ✅ *RAG Respostas com Embeddings (FAISS):* Ao utilizar as "keywords" de busca no chat ("Quais itens", "detalhe", etc).
- ✅ *Docker-compose e deploy:* Tudo pronto pra provisionamento em instâncias locais.

## Instruções de Instalação e Uso

### Utilizando Docker
A aplicação foi completamente "dockerizada" para garantir compatibilidade e reprodutibilidade de ambiente.

1. Crie o arquivo `.env` na **raiz do projeto** (junto do arquivo `docker-compose.yml`) com a sua chave da API da OpenAI:
   `OPENAI_API_KEY=sk-...`
2. Pelo terminal, na raiz do repositório (onde o arquivo `docker-compose.yml` está), execute os contêineres:
   ```bash
   docker-compose up --build
   ```
3. Acesse a plataforma pelo navegador: [http://localhost:3000](http://localhost:3000)
