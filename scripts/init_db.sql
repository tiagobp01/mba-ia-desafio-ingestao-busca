-- Habilitar extensão pgvector (obrigatório)
CREATE EXTENSION IF NOT EXISTS vector;

-- ──────────────────────────────────────────────
-- Tabela de empresas (dados brutos do PDF)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS companies (
    id           SERIAL PRIMARY KEY,
    name         TEXT        NOT NULL,
    revenue      NUMERIC(20, 2),
    founded_year INTEGER,
    created_at   TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- Índice para buscas por nome
CREATE INDEX IF NOT EXISTS idx_companies_name
    ON companies (name);

-- Índice para filtros por ano de fundação
CREATE INDEX IF NOT EXISTS idx_companies_founded_year
    ON companies (founded_year);

-- ──────────────────────────────────────────────
-- Tabelas do LangChain / pgVector
-- (criadas automaticamente pelo PGVector,
--  mas declaradas aqui para documentação)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS langchain_pg_collection (
    uuid      UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    name      TEXT    UNIQUE NOT NULL,
    cmetadata JSONB
);

CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
    uuid          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID    REFERENCES langchain_pg_collection (uuid) ON DELETE CASCADE,
    document      TEXT,
    cmetadata     JSONB,
    embedding     VECTOR(768),   -- Ajustado para a dimensão do Gemini (768 para embedding-001)
    custom_id     TEXT
);

-- Índice HNSW para busca por similaridade
CREATE INDEX IF NOT EXISTS idx_embedding_hnsw
    ON langchain_pg_embedding
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
