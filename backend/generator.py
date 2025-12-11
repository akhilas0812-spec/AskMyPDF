# backend/generator.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY missing in .env")

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
You are AskMyPDF: you must ONLY answer from the provided document chunks.
If the answer is not present, respond exactly: I cannot find this information in the document.
Do not hallucinate. Do not add any extra commentary.
"""

def generate_answer(query, retrieved_chunks):
    # retrieved_chunks: list of dicts with "chunk" key
    context = "\n\n".join([c["chunk"] for c in retrieved_chunks])
    prompt = f"""
User question:
{query}

Relevant PDF content:
{context}

Now answer ONLY using the above content. If the answer cannot be found in the content,
respond exactly with:
I cannot find this information in the document.
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.0
    )

    # Robust extraction for different SDK shapes
    try:
        return completion.choices[0].message.content
    except Exception:
        pass
    try:
        return completion.choices[0].message["content"]
    except Exception:
        pass
    try:
        return completion.choices[0].text
    except Exception:
        pass
    return str(completion)
