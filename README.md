# Desafio MBA Engenharia de Software com IA - Full Cycle

Este repositório contém a solução para o desafio de **Ingestão e Busca de Dados (RAG)**. O objetivo é construir um sistema que processa documentos PDF, armazena-os em um banco de dados vetorial e permite consultas semânticas através de uma interface de chat fundamentada no conteúdo do documento.

## 🚀 Tecnologias Utilizadas

- **Linguagem**: Python 3.12+
- **Framework de IA**: [LangChain](https://www.langchain.com/)
- **Banco de Dados Vetorial**: PostgreSQL com a extensão [pgvector](https://github.com/pgvector/pgvector)
- **Modelos de Linguagem**: OpenAI (GPT-4) ou Google Gemini
- **Processamento de PDF**: PyPDF
- **Infraestrutura**: Docker & Docker Compose

## 🛠️ Configuração do Ambiente

### 1. Pré-requisitos
- Docker e Docker Compose instalados.
- Python 3.12 ou superior.
- Uma chave de API (OpenAI ou Google Gemini).

### 2. Instalação de Dependências
Crie um ambiente virtual e instale as dependências:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env` e preencha as variáveis necessárias:
```powershell
cp .env.example .env
```
Campos principais:
- `OPENAI_API_KEY` ou `GOOGLE_API_KEY`
- `DATABASE_URL` (padrão configurado para o Docker)

### 4. Subir o Banco de Dados
Utilize o Docker Compose para iniciar o banco de dados PostgreSQL com suporte a vetores:
```powershell
docker-compose up -d
```

## 📂 Estrutura do Projeto

- `src/ingest.py`: Script responsável por ler o PDF, gerar chunks e salvar no banco de dados.
- `src/search.py`: Lógica de busca semântica e configuração do prompt do sistema.
- `src/chat.py`: Interface de linha de comando para interação com o chatbot.
- `document.pdf`: Documento base para a ingestão de dados.

## ⚙️ Orientações de Desenvolvimento

Para concluir o desenvolvimento deste desafio, siga os seguintes passos:

1.  **Ingestão de Dados (`ingest.py`)**:
    - Utilize o `PyPDFLoader` para carregar o arquivo `document.pdf`.
    - Divida o documento em partes menores usando `RecursiveCharacterTextSplitter` (sugerido: chunk_size=1000, chunk_overlap=200).
    - Configure a persistência no PostgreSQL usando `PGVector` e o modelo de embeddings escolhido.

2.  **Busca e Recuperação (`search.py`)**:
    - Implemente a função `search_prompt` para retornar uma chain do LangChain.
    - Utilize o template de prompt já definido no arquivo, garantindo que o modelo siga estritamente o contexto fornecido.
    - Configure o retriever para buscar as informações mais relevantes no banco vetorial.

3.  **Interface de Chat (`chat.py`)**:
    - Implemente um loop que recebe a entrada do usuário e exibe a resposta do modelo.
    - Garanta que o histórico de conversa ou o contexto seja passado corretamente para a chain.

## 🏃 Como Executar

### Ingestão
Para processar o documento e alimentar o banco de dados:
```powershell
python src/ingest.py
```

### Chat
Para iniciar a interação com o assistente:
```powershell
python src/chat.py
```

---
*Desenvolvido como parte do MBA em Engenharia de Software com IA.*