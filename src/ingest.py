import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
PDF_PATH = os.getenv("PDF_PATH")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")

def ingest_pdf():
    if not os.path.exists(PDF_PATH):
        print(f"Erro: Arquivo {PDF_PATH} não encontrado.")
        return

    print(f"Carregando {PDF_PATH}...")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    print("Dividindo o texto em pedaços...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=True
    )
    all_splits = text_splitter.split_documents(documents)

    print(f"Criando embeddings e armazenando no banco de dados ({len(all_splits)} pedaços)...")
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )
    
    vector_store.add_documents(all_splits)
    print("Ingestão concluída com sucesso!")

if __name__ == "__main__":
    ingest_pdf()