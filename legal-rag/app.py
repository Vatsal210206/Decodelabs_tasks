import pdfplumber
import google.generativeai as genai

pages = []

with pdfplumber.open("contract.pdf") as pdf:

    for page_num, page in enumerate(pdf.pages):

        text = page.extract_text()

        if text:

            pages.append({
                "page": page_num + 1,
                "text": text
            })

print(pages[0])
chunks = []

for item in pages:

    page_num = item["page"]

    text = item["text"]

    chunk_size = 1000

    for i in range(0, len(text), chunk_size):

        chunk = text[i:i+chunk_size]

        chunks.append({
            "page": page_num,
            "text": chunk
        })

results = []

for chunk in chunks:

    question = input("Ask a question: ").lower()
    results = []

for chunk in chunks:

    if any(word in chunk["text"].lower() for word in question.split()):

        results.append(chunk)

if results:

    print("Results Found:")
    print(results[0]["text"])
    print("Page:", results[0]["page"])

else:

    print("No matching clause found.")
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
model = genai.GenerativeModel("gemini-2.5-flash")
context = results[0]["text"]
prompt = f"""
Answer ONLY using the context.

If answer is not found,
say:

Not found in document.

Context:
{context}

Question:
What is the notice period?
"""
response = model.generate_content(prompt)

print("\n========== ANSWER ==========\n")

print(response.text)

print("\n========== CITATION ==========\n")

print("Source Page:", results[0]["page"])

print("\nEvidence:")

print(results[0]["text"])