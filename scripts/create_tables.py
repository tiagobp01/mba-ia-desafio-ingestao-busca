import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/rag",
).replace("postgresql+psycopg://", "postgresql://")

CREATE_EXTENSION_SQL = "CREATE EXTENSION IF NOT EXISTS vector;"

CREATE_COMPANIES_SQL = """
CREATE TABLE IF NOT EXISTS companies (
    id           SERIAL PRIMARY KEY,
    name         TEXT        NOT NULL,
    revenue      NUMERIC(20, 2),
    founded_year INTEGER,
    created_at   TIMESTAMP   NOT NULL DEFAULT NOW()
);
"""

CREATE_COLLECTION_SQL = """
CREATE TABLE IF NOT EXISTS langchain_pg_collection (
    uuid      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name      TEXT UNIQUE NOT NULL,
    cmetadata JSONB
);
"""

CREATE_EMBEDDING_SQL = """
CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
    uuid          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID REFERENCES langchain_pg_collection (uuid) ON DELETE CASCADE,
    document      TEXT,
    cmetadata     JSONB,
    embedding     VECTOR(768),
    custom_id     TEXT
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_embedding_hnsw
    ON langchain_pg_embedding
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
"""


def create_tables():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        steps = [
            ("Extensão pgvector",          CREATE_EXTENSION_SQL),
            ("Tabela companies",            CREATE_COMPANIES_SQL),
            ("Tabela langchain_pg_collection", CREATE_COLLECTION_SQL),
            ("Tabela langchain_pg_embedding",  CREATE_EMBEDDING_SQL),
            ("Índice HNSW",                CREATE_INDEX_SQL),
        ]

        for label, sql in steps:
            cursor.execute(sql)
            print(f"[OK] {label}")

        cursor.close()
        conn.close()
        print("\nTodas as tabelas foram criadas com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao criar tabelas: {e}")


if __name__ == "__main__":
    create_tables()
