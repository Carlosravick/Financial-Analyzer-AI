<h1 align="center">
  📊 Financial Analyzer AI
</h1>

<p align="center">
  <em>Plataforma de Inteligência Financeira com IA baseada em Clean Architecture.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

---

## 🎥 Apresentação do Projeto

Confira o vídeo de apresentação e explicação técnica do projeto no YouTube: 
[![Demonstração do Projeto](https://img.youtube.com/vi/MfuscmHL1eA/0.jpg)](https://youtu.be/MfuscmHL1eA)

🔗 **Link direto para o vídeo:** [https://youtu.be/MfuscmHL1eA](https://youtu.be/MfuscmHL1eA)

---

## 🏗️ Visão Geral e Arquitetura

O **Financial Analyzer AI** foi desenvolvido utilizando os conceitos de **Clean Architecture** (Separação de Responsabilidades), e conta com as seguintes ferramentas e tecnologias:

- 🐍 **Backend:** Python + FastAPI, encapsulando a lógica de Ingestão de Dados (Pandas), e Inteligência Artificial.
- ⚛️ **Frontend:** Next.js + React.js, provendo uma interface limpa com renderização de gráficos, análise preditiva e Chat RAG. O código segue os princípios de **Clean Code**, sendo fortemente tipado com TypeScript, utilizando separação de componentes lógicos (`src/components`), isolamento da camada de serviços de API (`src/services`), e variáveis de ambiente configuráveis (`.env.local`).
- 🧠 **IA Stack:** Diferenciei a aplicação implementando um sistema com Roteamento Inteligente (*Smart Router*). Diferente de usar apenas um Agente, a API envia a pergunta do usuário para o **FAISS (Vetor semântico Embeddings de Busca RAG)**, caso ele precise de descrições e itens contábeis, ou usa um engine **Pandas DataFrame Agent** da OpenAI (Functions), se forem cálculos e consolidações exatas, evitando alucinações nas contas de agregação.

## 🛠️ Decisões Técnicas

1. **Uso do Modelo `gpt-4o-mini`:** Focado na eficiência técnica e de custos (Tokens). Ele é incrivelmente rápido e extremamente eficiente em seguir as guidelines rigorosas passadas pelo "System Prompt" no Pandas Agent, enquanto nos poupa dinheiro nos requests repetitivos de Embeddings.
2. **Separação de Rotas Modulares:** O backend foi estruturado em módulos independentes (`data_engine.py`, `ai_engine.py`, `models.py`) para facilitar a manutenção, clareza e evolução do código, evitando que lógicas complexas fiquem todas agrupadas no arquivo principal.
3. **Parsing de Excel / CSV Complexo:** O Worker no serviço de Data Engine extrai BOMs (\ufeff), lida com planilhas que estouram delimitadores (CSV ';' vs ',') e padroniza a formatação contábil para Float exato antes mesmo do LLM encostar nela.
4. **Insights Proativos (Automáticos):** Ao fazer o Upload, o backend executa _zero-shot processing_ onde analisa a situação macro da empresa com base no resumo processado, exibindo dicas ativas no front (ex: controle de inadimplência), em vez de apenas agendar o RAG ou depender do chat.
5. **Clean Code no Frontend:** O Frontend em Next.js foi estruturado isolando responsabilidades, removendo acoplamento forte entre UI e regras de chamadas de API (isoladas em `src/services/api.ts`). Todo o projeto é estritamente tipado (Interfaces TypeScript em `src/types`), garantindo estabilidade e escalabilidade, e centralizando credenciais (com o uso de `.env.local`).

## ✨ Funcionalidades Entregues

- ✅ **Processamento de Dados Financeiros:** Agora lida com CSV e XLSX nativamente e gera Uploads para análises avançadas.
- ✅ **Métricas e Insights Automáticos:** Dashboard reativo gerando receita, ticket, inadimplência + Dicas de IA e Gráfico Temporal (`recharts`).
- ✅ **RAG Respostas com Embeddings (FAISS):** Respostas semânticas ao utilizar "keywords" de busca no chat ("Quais itens", "detalhe", etc).
- ✅ **Deploy Descomplicado:** Tudo pronto pra provisionamento via Docker e `docker-compose`.

## 🚀 Instruções de Instalação e Uso

A aplicação foi completamente "dockerizada" para garantir compatibilidade e reprodutibilidade do ambiente em qualquer máquina.

### Passos:

1. **Configure as Variáveis de Ambiente:** Crie o arquivo `.env` na **raiz do projeto** (junto do arquivo `docker-compose.yml`) com a sua chave da API da OpenAI. Exemplo:
   ```env
   OPENAI_API_KEY=sk-...
   ```

2. **Inicie os Contêineres:** Pelo terminal, na raiz do repositório, execute:
   ```bash
   docker-compose up --build
   ```

3. **Acesse a Aplicação:** Após o build, acesse a plataforma pelo navegador: 
   👉 [http://localhost:3000](http://localhost:3000)
