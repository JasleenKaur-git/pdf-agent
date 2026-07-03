import streamlit as st
import os
from ingest import ingest_pdf, clear_all_documents
from query import ask_question

st.set_page_config(page_title="PDF Q&A Agent", page_icon="📄")

st.title("📄 PDF Q&A Agent")
st.write("Upload PDFs, then ask questions about them.")

# ---- Upload Section ----
st.header("1. Upload Documents")
uploaded_files = st.file_uploader(
    "Choose PDF files",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Process PDFs"):
        for uploaded_file in uploaded_files:
            save_path = os.path.join("pdfs", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner(f"Processing {uploaded_file.name}..."):
                result = ingest_pdf(save_path)

            if result["status"] == "skipped":
                st.info(f"{result['filename']} already processed, skipping.")
            else:
                st.success(f"{result['filename']} — {result['chunks']} chunks stored.")

st.divider()

# ---- Query Section ----
st.header("2. Ask a Question")
question = st.text_input("Your question:")

if st.button("Get Answer"):
    if question:
        with st.spinner("Searching documents..."):
            result = ask_question(question)
        st.session_state["last_answer"] = result
    else:
        st.warning("Please type a question first.")

if "last_answer" in st.session_state:
    result = st.session_state["last_answer"]
    st.write(result["answer"])

    if result["sources"]:
        with st.expander("Sources used"):
            for s in result["sources"]:
                st.write(f"- {s['filename']}, page {s['page']}")

    if st.button("🎙️ Read answer aloud"):
        with st.spinner("Generating audio..."):
            from query import text_to_speech
            audio_path = text_to_speech(result["answer"])
        with open(audio_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
    else:
        st.warning("Please type a question first.")

st.divider()

# ---- Clear Section ----
st.header("3. Clear Documents")
st.write("Use this before the next person uses the app.")
if st.button("Clear all documents", type="secondary"):
    clear_all_documents()
    st.success("All documents cleared.")