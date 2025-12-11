# app.py — fixed complete file (minimal, safe). Paste this to replace your current app.py
import streamlit as st
import os
import tempfile
import time
import hashlib
from backend.ingest import ingest_pdf
from backend.retriever import load_chunks, retrieve_relevant_chunks
from backend.generator import generate_answer

st.set_page_config(page_title="AskMyPDF", page_icon="📄", layout="centered")

# Load CSS if present (keeps premium styling)
if os.path.exists("style.css"):
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# === Session state initialization ===
if "uploaded" not in st.session_state:
    st.session_state["uploaded"] = False
if "processed" not in st.session_state:
    st.session_state["processed"] = False
if "chunks_path" not in st.session_state:
    st.session_state["chunks_path"] = "data/chunks.json"
if "last_response" not in st.session_state:
    st.session_state["last_response"] = ""
if "last_action" not in st.session_state:
    st.session_state["last_action"] = ""  # "answer" or "summary"
if "uploaded_file_info" not in st.session_state:
    # (name, size, sha256)
    st.session_state["uploaded_file_info"] = None

st.title("AskMyPDF")
st.markdown("Upload a PDF, then ask a question or click **Summarize PDF**. The assistant answers **only** from the uploaded document.")

# === Helper: read uploaded file info safely and reset pointer ===
def _get_file_info(u):
    """
    Return (name, size, sha256) for the uploaded file.
    This reads the bytes but resets the file pointer so Streamlit can still read it afterwards.
    """
    name = getattr(u, "name", "uploaded.pdf")
    data = None
    size = None
    sha = None
    try:
        # try to access buffer (UploadedFile supports this)
        buf = u.getbuffer()
        data = buf.tobytes()
    except Exception:
        try:
            # fallback: read whole file, then seek back to start
            try:
                u.seek(0)
            except Exception:
                pass
            data = u.read()
        except Exception:
            data = None

    if data is not None:
        size = len(data)
        sha = hashlib.sha256(data).hexdigest()
        # IMPORTANT: reset stream pointer so later code can read the file from start
        try:
            u.seek(0)
        except Exception:
            pass

    return (name, size, sha)

# === Upload + Auto-Ingest (temp file) ===
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    current_info = _get_file_info(uploaded_file)

    # Only process if it's a new upload (prevents re-processing on reruns)
    if st.session_state["uploaded_file_info"] != current_info:
        # write uploaded file to a temp file (so nothing required in project folder)
        try:
            # ensure pointer at start before reading to temp file
            try:
                uploaded_file.seek(0)
            except Exception:
                pass

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
                temp_path = tf.name
                tf.write(uploaded_file.read())
        except Exception as e:
            st.error(f"Failed to write uploaded PDF to temp file: {e}")
            temp_path = None

        if temp_path:
            # reset previous response because this is a new document
            st.session_state["last_response"] = ""
            st.session_state["last_action"] = ""
            st.session_state["uploaded"] = True
            st.session_state["processed"] = False

            # ingest the temp file into data/chunks.json used by the app
            try:
                # remove any stale chunks file so ingest always creates fresh content
                try:
                    if os.path.exists(st.session_state["chunks_path"]):
                        os.remove(st.session_state["chunks_path"])
                except Exception:
                    pass

                cnt = ingest_pdf(temp_path, output_json=st.session_state["chunks_path"])
                st.session_state["processed"] = True

                # force-clear any cached items that might hold old embeddings
                st.session_state.pop("chunks_cached", None)
                st.session_state.pop("retriever", None)

                # save the uploaded file info so we won't reprocess on reruns
                st.session_state["uploaded_file_info"] = current_info

                # success message
                st.markdown("""
                <div class="success-box">
                    <div class="success-icon">✔</div>
                    <div>PDF uploaded successfully. You can now ask questions.</div>
                </div>
                """, unsafe_allow_html=True)

                # remove the temporary file (we have chunks stored now)
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

            except Exception as e:
                st.session_state["processed"] = False
                st.error(f"Error processing uploaded PDF: {e}")
                # try to remove temp file on failure
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

# === Input: question and action buttons (Get Answer + Summarize side-by-side) ===
query = st.text_input("Ask a question about the document:")

col1, col2 = st.columns([1, 1])
get_btn = col1.button("Get Answer")
summ_btn = col2.button("Summarize PDF")

# === Helper functions ===
def run_get_answer(user_query):
    # load fresh chunks from disk every time (no caching)
    chunks = load_chunks(st.session_state["chunks_path"])
    retrieved = retrieve_relevant_chunks(user_query, chunks, top_k=5)
    answer = generate_answer(user_query, retrieved)
    return answer

def run_summarize():
    chunks = load_chunks(st.session_state["chunks_path"])
    full_text = "\n".join(chunks)
    # use generate_answer with a summarization instruction and the full_text as chunk
    summary = generate_answer("Summarize this document in 5 concise bullet points.", [{"chunk": full_text}])
    return summary

# === Actions ===
if get_btn:
    if not st.session_state["uploaded"]:
        st.error("Please upload a PDF first.")
    elif not st.session_state["processed"]:
        st.error("PDF is still being processed. Please wait or re-upload.")
    elif not query.strip():
        st.error("Please type a question.")
    else:
        with st.spinner("Retrieving answer from document..."):
            resp = run_get_answer(query)
        st.session_state["last_response"] = resp
        st.session_state["last_action"] = "answer"

if summ_btn:
    if not st.session_state["uploaded"]:
        st.error("Please upload a PDF first.")
    elif not st.session_state["processed"]:
        st.error("PDF is still being processed. Please wait or re-upload.")
    else:
        with st.spinner("Summarizing document..."):
            resp = run_summarize()
        st.session_state["last_response"] = resp
        st.session_state["last_action"] = "summary"

# === Results area (single, clean display) ===
if st.session_state["last_response"]:
    st.markdown("---")
    title = "Answer" if st.session_state["last_action"] == "answer" else "Summary"
    st.subheader(title)
    st.write(st.session_state["last_response"])

    # Download button for response
    st.download_button(
        label="Download response as TXT",
        data=st.session_state["last_response"],
        file_name=f"askmypdf_{st.session_state['last_action']}.txt",
        mime="text/plain"
    )
