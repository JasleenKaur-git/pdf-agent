import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client
from groq import Groq

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


def ask_question(question, match_threshold=0.55, match_count=5):
    """Takes a question, returns a dict with the answer text and the matched sources."""
    question_embedding = embedding_model.encode(question).tolist()

    result = supabase.rpc("match_documents", {
        "query_embedding": question_embedding,
        "match_threshold": match_threshold,
        "match_count": match_count
    }).execute()

    matches = result.data

    if not matches:
        return {"answer": "No relevant information found in the documents.", "sources": []}

    context = "\n\n".join([
        f"[Source: {m['metadata']['filename']}, Page {m['metadata']['page']}]\n{m['content']}"
        for m in matches
    ])

    prompt = f"""Answer the question based only on the context below.
After your answer, mention which source(s) (filename and page) you used.

Context:
{context}

Question: {question}

Answer:"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    sources = [{"filename": m['metadata']['filename'], "page": m['metadata']['page']} for m in matches]

    return {"answer": response.choices[0].message.content, "sources": sources}

def text_to_speech(text):
    """Converts text to speech and saves as audio file. Returns the file path."""
    from gtts import gTTS
    import tempfile
    
    tts = gTTS(text=text, lang='en', slow=False)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(temp_file.name)
    
    return temp_file.name


if __name__ == "__main__":
    question = input("Ask a question about your PDF: ")
    result = ask_question(question)
    print(f"\n{result['answer']}")