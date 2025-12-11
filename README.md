# AskMyPDF

A minimal, fast, and accurate PDF-Question Answering application built with Streamlit and OpenAI.
The system extracts text from uploaded PDFs, chunks it, embeds it, and answers questions strictly based on the document — without hallucinations.

## Features

* Upload a PDF and ask precise questions
* Answers generated strictly from the uploaded PDF
* Fast embeddings + retrieval for accuracy
* Clean, minimal UI
* Summarize the entire PDF
* Download generated responses
* Automatic chunk regeneration for every upload
* No hallucinations: model only uses PDF content


## Tech Stack

* **Python 3.10+**
* **Streamlit** for UI
* **OpenAI API** for embeddings + responses
* **PyPDF2** for PDF text extraction
* **SentenceTransformers / HuggingFace** for embedding model
* **FAISS-style in-memory similarity search**


## Project Structure

```
AskMyPDF/
│
├── app.py                 # Main Streamlit app
├── style.css              # UI styling (minimal + custom)
├── .env                   # API Key (not included)
│
├── backend/
│   ├── ingest.py          # PDF text extraction + chunking
│   ├── retriever.py       # Embedding + similarity search
│   └── generator.py       # Generates answers from retrieved chunks
│
├── components/
│   ├── highlight.js       # Client-side text highlighter (optional)
│   └── pdf_viewer.html    # PDF preview component
│
├── data/
│   └── chunks.json        # Auto-generated chunk file (updated per upload)
│── requirements.txt       # Python dependencies
```


## Installation

### 1. Clone the repository

```
git clone https://github.com/your-username/AskMyPDF.git
cd AskMyPDF
```

### 2. Create and activate a virtual environment

```
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Add API Key

Create a **.env** file in the project root:

```
OPENAI_API_KEY=your_key_here
```


## Run the Application

```
streamlit run app.py
```

The app will open in your browser:

```
http://localhost:8501
```


## Working

### 1. **Upload a PDF**

The system extracts text and creates semantic chunks.
Each upload regenerates `chunks.json`, ensuring answers always reflect the latest PDF.

### 2. **Ask a Question**

Your query is embedded and compared against document embeddings.

### 3. **Retrieve Relevant Chunks**

Top-similarity chunks are returned.

### 4. **Answer Generation**

The model receives ONLY the retrieved text and your question.
No hallucinations, the answers are tied strictly to PDF content.


## Requirements

```
streamlit
openai
PyPDF2
sentence-transformers
numpy
python-dotenv
```

## Notes

* No user history is stored.
* PDF content is processed locally except model calls.
* Each new upload overwrites previous chunks, ensuring isolated results.

