import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

def ingest_pdf(pdf_path):
    """Ingests a single PDF file into Supabase. Returns number of chunks stored, or 0 if skipped."""
    filename = os.path.basename(pdf_path)

    existing = supabase.table("documents").select("id").eq("metadata->>filename", filename).limit(1).execute()
    if existing.data:
        return {"filename": filename, "status": "skipped", "chunks": 0}

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    chunks = splitter.split_documents(pages)

    for chunk in chunks:
        text = chunk.page_content
        page_number = chunk.metadata.get("page", "unknown")
        embedding = embedding_model.encode(text).tolist()

        supabase.table("documents").insert({
            "content": text,
            "metadata": {"filename": filename, "page": page_number},
            "embedding": embedding
        }).execute()

    return {"filename": filename, "status": "ingested", "chunks": len(chunks)}


def clear_all_documents():
    """Deletes every row in the documents table."""
    supabase.table("documents").delete().neq("id", 0).execute()


if __name__ == "__main__":
    pdf_files = glob.glob("pdfs/*.pdf")
    print(f"Found {len(pdf_files)} PDF(s)\n")
    for pdf_path in pdf_files:
        result = ingest_pdf(pdf_path)
        if result["status"] == "skipped":
            print(f"Skipping {result['filename']} — already ingested")
        else:
            print(f"Stored {result['chunks']} chunks from {result['filename']}")
    print("\nAll PDFs processed!")