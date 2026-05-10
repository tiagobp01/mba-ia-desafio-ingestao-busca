"""
src/ingest.py
─────────────
Ingestão do document.pdf no PostgreSQL com pgVector.

Fluxo:
  1. Carrega o PDF com PyPDFLoader
  2. Divide em chunks (1000 chars, overlap 150)
  3. Gera embeddings (Google Gemini embedding-001)
  4. Salva vetores no pgVector via LangChain
  5. Extrai dados estruturados e popula a tabela `companies`
"""

import os
import re
import psycopg2
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

# ── Configurações ─────────────────────────────────────────────────────────────

PDF_PATH       = os.getenv("PDF_PATH", "document.pdf")
DATABASE_URL   = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
)
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "document_embeddings")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")

CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 150

# ── Embeddings ────────────────────────────────────────────────────────────────

embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

# ── Funções auxiliares ────────────────────────────────────────────────────────

def load_pdf(path: str):
    """Carrega o PDF e retorna lista de Documents do LangChain."""
    print(f"[1/4] Carregando PDF: {path}")
    if not os.path.exists(path):
        print(f"      → [ERRO] Arquivo {path} não encontrado.")
        return []
    loader = PyPDFLoader(path)
    documents = loader.load()
    print(f"      → {len(documents)} página(s) carregada(s).")
    return documents


def split_documents(documents):
    """Divide os Documents em chunks menores."""
    print(f"[2/4] Dividindo em chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )
    chunks = splitter.split_documents(documents)
    print(f"      → {len(chunks)} chunk(s) gerado(s).")
    return chunks


def store_vectors(chunks):
    """Gera embeddings e armazena no pgVector."""
    print("[3/4] Gerando embeddings e salvando no pgVector...")
    try:
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=DATABASE_URL,
            use_jsonb=True,
        )
        
        vector_store.add_documents(chunks)
        print(f"      → {len(chunks)} vetores armazenados na coleção '{COLLECTION_NAME}'.")
        return vector_store
    except Exception as e:
        print(f"      → [ERRO] Falha ao armazenar vetores: {e}")
        return None


def parse_company_row(line: str):
    """
    Tenta extrair (nome, faturamento, ano) de uma linha do PDF.
    Exemplo: SuperTechIA  R$ 10.000.000,00  2020
    """
    # Padrão: Nome | R$ Valor | Ano
    pattern = r"^(.+?)\s+R\$\s*([\d.,]+)\s+(\d{4})\s*$"
    match = re.match(pattern, line.strip())
    if not match:
        return None

    name = match.group(1).strip()
    # Converte faturamento para float
    raw_revenue = match.group(2).replace(".", "").replace(",", ".")
    try:
        revenue = float(raw_revenue)
    except ValueError:
        revenue = None

    try:
        founded_year = int(match.group(3))
    except ValueError:
        founded_year = None

    return (name, revenue, founded_year)


def populate_companies_table(documents):
    """
    Extrai os dados estruturados do PDF e popula a tabela `companies`.
    """
    print("[4/4] Populando tabela `companies` com dados estruturados...")

    try:
        # Conecta sem o prefixo "+psycopg"
        raw_url = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
        conn = psycopg2.connect(raw_url)
        cursor = conn.cursor()

        # Limpa dados anteriores
        cursor.execute("TRUNCATE TABLE companies RESTART IDENTITY;")

        rows_inserted = 0
        header_keywords = {"nome", "faturamento", "fundação", "empresa", "fundacao"}

        for doc in documents:
            for line in doc.page_content.splitlines():
                if any(kw in line.lower() for kw in header_keywords):
                    continue

                parsed = parse_company_row(line)
                if parsed:
                    cursor.execute(
                        """
                        INSERT INTO companies (name, revenue, founded_year)
                        VALUES (%s, %s, %s)
                        """,
                        parsed,
                    )
                    rows_inserted += 1

        conn.commit()
        cursor.close()
        conn.close()
        print(f"      → {rows_inserted} empresa(s) inserida(s) na tabela `companies`.")
    except Exception as e:
        print(f"      → [ERRO] Falha ao popular tabela companies: {e}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Ingestão do PDF — RAG com LangChain + pgVector")
    print("=" * 55)

    documents = load_pdf(PDF_PATH)
    if not documents:
        return
        
    chunks    = split_documents(documents)
    store_vectors(chunks)
    populate_companies_table(documents)

    print("\n[✓] Ingestão concluída com sucesso!")
    print(f"    Coleção vetorial : {COLLECTION_NAME}")
    print(f"    Tabela estruturada: companies")


if __name__ == "__main__":
    main()