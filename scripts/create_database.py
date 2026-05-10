import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER     = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST     = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT     = os.getenv("POSTGRES_PORT", "5432")
# Extrai o nome do banco da URL se necessário, ou usa o padrão
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag")
POSTGRES_DB = os.getenv("PG_VECTOR_DB_NAME", "rag")

def create_database_if_not_exists():
    """Conecta ao postgres padrão e cria a database alvo se ela não existir."""
    try:
        conn = psycopg2.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (POSTGRES_DB,),
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f'CREATE DATABASE "{POSTGRES_DB}"')
            print(f"[OK] Database '{POSTGRES_DB}' criada com sucesso.")
        else:
            print(f"[INFO] Database '{POSTGRES_DB}' já existe. Nenhuma ação necessária.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERRO] Falha ao criar banco de dados: {e}")

if __name__ == "__main__":
    create_database_if_not_exists()
