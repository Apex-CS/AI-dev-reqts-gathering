import os
import io
from typing import Dict

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import docx
from fpdf import FPDF
import markdown
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Apex Systems AI",
    page_icon="https://www.apexsystems.com/profiles/apex/themes/apex_bootstrap/favicon.ico",
    layout="wide",
    menu_items={
        'About': (
            "# Apex Systems AI \n"
            "A demo application showcasing AI capabilities for requirements gathering.\n")
    }
)

# --- Constants and Config ---
load_dotenv()
DEFAULT_SESSION_STATE = {
    "LLM_MODEL_NAME": "apex-demos-gpt-4o",
    "LLM_MODEL_TEMPERATURE": 0.0,
    "messages": [],
    "chat_history_store": {},
    "doc_added": False
}
DOCX_TYPES = [
    "application/docx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

# --- Session State Initialization ---
for key, value in DEFAULT_SESSION_STATE.items():
    st.session_state.setdefault(key, value)

_store: Dict[str, InMemoryChatMessageHistory] = st.session_state["chat_history_store"]

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    return _store.setdefault(session_id, InMemoryChatMessageHistory())

def construct_model(model_name, temperature):
    return AzureChatOpenAI(
        azure_deployment=model_name,
        temperature=temperature,
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
    )

model = construct_model(st.session_state.LLM_MODEL_NAME, st.session_state.LLM_MODEL_TEMPERATURE)

# --- Prompt Templates ---
template = """
Answer the following question: {question}
use {documents} to help answer the question.
"""

initial_template = """
You are a highly skilled Software Architect. Your task is to analyze the provided transcription to extract software requirements, identify potential issues, and gather all relevant context.

Please use the following transcription as your source material:
{documents}

Your response should include:
1. A detailed summary of the transcription.
2. A list of identified requirements and any ambiguities or issues found.
3. Suggestions for possible improvements or changes.
4. A set of proposed User Stories, each with:
    - Title
    - Description
    - Acceptance Criteria

Present your analysis in a clear, organized, and professional manner.
"""

prompt = ChatPromptTemplate.from_template(template)
chain_with_history = RunnableWithMessageHistory(model, get_session_history)

# --- Utility Functions ---
def safe_text(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

def extract_text_from_docx(file_bytes):
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file_bytes):
    # Placeholder: PDF text extraction should use a library like PyPDF2 or pdfplumber
    # For now, just decode as utf-8 (not reliable for real PDFs)
    return file_bytes.decode("utf-8", errors="ignore")

def render_messages(messages):
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def export_chat_to_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for message in messages:
        role = message["role"].capitalize()
        html = markdown.markdown(message["content"])
        soup = BeautifulSoup(html, "html.parser")
        content = soup.get_text()
        pdf.multi_cell(0, 10, safe_text(f"{role}:\n{content}\n"), align="L")
        pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- Streamlit App Logic ---
def main():
    st.title("Apex AI Requirements Gathering")
    if st.session_state.doc_added:
        st.info("Document added. You can now ask questions related to the document.")
        handle_user_input()
    else:
        st.warning("Please upload a document to get started.")
        handle_file_upload()

def handle_file_upload():
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx"])
    documents = ""
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            documents = extract_text_from_pdf(uploaded_file.read())
        elif uploaded_file.type in DOCX_TYPES:
            documents = extract_text_from_docx(uploaded_file.read())
    submit = st.button("Submit")
    if submit and uploaded_file:
        prompt_text = initial_template.format(documents=documents)
        response = chain_with_history.invoke(
            prompt_text,
            config={"configurable": {"session_id": "global"}}
        )
        get_session_history("global").add_message(prompt_text)
        add_message("user", prompt_text)
        add_message("assistant", response.content)
        get_session_history("global").add_message(response)
        st.info("Document added. You can now ask questions related to the document.")
        st.session_state.doc_added = True
        handle_user_input()

def handle_user_input():
    render_messages(st.session_state.messages)
    user_input = st.chat_input(
        "Type your message here...",
        accept_file=True,
        file_type=["pdf", "docx"],
    )
    documents = ""
    if user_input:
        # Handle file attachments
        for file in getattr(user_input, "files", []):
            if file.type == "application/pdf":
                documents += extract_text_from_pdf(file.read())
            elif file.type in DOCX_TYPES:
                documents += extract_text_from_docx(file.read())
        question = getattr(user_input, "text", user_input)
        add_message("user", question)
        prompt_text = template.format(question=question, documents=documents)
        response = chain_with_history.invoke(
            prompt_text,
            config={"configurable": {"session_id": "global"}}
        )
        get_session_history("global").add_message(prompt_text)
        add_message("assistant", response.content)
        get_session_history("global").add_message(response)
        render_messages(st.session_state.messages)
    if st.button("Export Chat to PDF"):
        pdf_output = export_chat_to_pdf(st.session_state.messages)
        st.download_button(
            label="Download Chat as PDF",
            data=pdf_output,
            file_name="chat_history.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()