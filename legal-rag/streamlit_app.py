import streamlit as st
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv
import os
from vector_store import (
    store_chunks,
    retrieve_chunks
)
# Gemini Setup

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")

st.title("Legal Contract Assistant")

uploaded_file = st.file_uploader(
"Upload Contract",
type=["pdf"]
)

question = st.text_input(
"Ask a question about the contract"
)

pages = []
chunks = []

# Extract PDF

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text()

            if page_text:
                pages.append({
                    "page": page_num + 1,
                    "text": page_text
                })

# Create chunks
for item in pages:

    page_num = item["page"]
    text = item["text"]

    chunk_size = 1000

    for i in range(0, len(text), chunk_size):

        chunk = text[i:i + chunk_size]

        chunks.append({
            "page": page_num,
            "text": chunk
        })
if chunks:
        store_chunks(chunks)
        full_text = ""

for item in pages:
    full_text += item["text"] + "\n"

if st.button("Submit"):


    if uploaded_file is None:

        st.error("Please upload a PDF first.")

    else:

        results = retrieve_chunks(question)

    if not results:
        st.error("No matching clause found.")
    else:
        context = "\n\n".join(
            results["documents"][0]
        )
        prompt = f"""
Answer ONLY using the context below.

If answer is not found,
say 'Not found in document.

Context:
{context}

Question:
{question}
"""
        response = model.generate_content(prompt)
        st.session_state["last_question"] = question
        st.session_state["last_answer"] = response.text
        st.session_state["last_page"] = results["metadatas"][0][0]["page"]

        st.subheader("Answer")
        st.write(response.text)

        st.subheader("Source Page")
        st.write(
            results["metadatas"][0][0]["page"]
        )
        st.subheader("Evidence")
        st.write(
            results["documents"][0][0]
        )

if st.button("Generate Summary Dashboard"):
    dates_prompt = f"""
Extract all important dates from the document.

Return bullet points only.

Document:

{full_text}
"""

    stakeholder_prompt = f"""
Identify all stakeholders, companies,
organizations or parties involved.

Return bullet points only.

Document:

{full_text}
"""

    risk_prompt = f"""
Identify important legal risks,
liabilities and obligations.

Return bullet points only.

Document:

{full_text}
"""

    dates_response = model.generate_content(
        dates_prompt
    )

    stakeholder_response = model.generate_content(
        stakeholder_prompt
    )

    risk_response = model.generate_content(
        risk_prompt
    )
    st.session_state["dates"] = dates_response.text
    st.session_state["stakeholders"] = stakeholder_response.text
    st.session_state["risks"] = risk_response.text
    st.header("Summary Dashboard")

    st.subheader("📅 Important Dates")
    st.write(dates_response.text)

    st.subheader("👥 Stakeholders")
    st.write(stakeholder_response.text)

    st.subheader("⚠ Risks & Obligations")
    st.write(risk_response.text)
if st.button("Generate Report"):

    report = f"""
LEGAL CONTRACT ANALYSIS REPORT

=================================

Question:
{st.session_state.get('last_question', 'N/A')}

Answer:
{st.session_state.get('last_answer', 'N/A')}

Source Page:
{st.session_state.get('last_page', 'N/A')}

=================================

IMPORTANT DATES

{st.session_state.get('dates', 'No data available')}

=================================

STAKEHOLDERS

{st.session_state.get('stakeholders', 'No data available')}

=================================

RISKS

{st.session_state.get('risks', 'No data available')}
"""

    st.session_state["report"] = report

    st.success("Report Generated Successfully")
if "report" in st.session_state:

  st.download_button(
        label="Download Report",
        data=st.session_state["report"],
        file_name="contract_report.txt",
        mime="text/plain"
    )