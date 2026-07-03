# PDF Q&A Agent

A RAG (Retrieval-Augmented Generation) agent that lets you upload PDFs, ask questions about them, and get cited answers with optional text-to-speech.

## What it does
- Upload multiple PDFs through a web UI
- Ask questions in natural language
- Get answers with source citations (filename + page number)
- Read answers aloud via text-to-speech

## Tech Stack
- **LangChain** — RAG pipeline framework
- **sentence-transformers** — local embeddings (all-MiniLM-L6-v2)
- **Supabase pgvector** — vector database
- **Groq** — LLM for answer generation
- **Streamlit** — web UI
- **gTTS** — text-to-speech

## How to run
1. Clone the repo
2. Create a `.env` file with your `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`
3. Create a venv with Python 3.11 and install requirements
4. Run `python -m streamlit run app.py`