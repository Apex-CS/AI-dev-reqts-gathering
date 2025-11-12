import os
from typing import List, Optional, Dict

from pydantic import BaseModel, Field

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

from langchain.chat_models.base import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI

from langchain_core.chat_history import InMemoryChatMessageHistory

from src.functions.settings import get_llm_settings

# --- Model Configurations ---

class LLMModelConfig(BaseModel):
    name: str = Field(..., alias="model_name")
    temperature: float

MODEL_MAPPINGS: Dict[str, str] = {
    "apex-demos-gpt-4-32k": "Azure GPT-4 32k",
    "apex-demos-gpt-4o": "Azure GPT-4o",
}

ANTHROPIC_MODELS = {
    "claude-instant-1.2",
    "claude-2.0",
    "claude-2.1",
    "claude-3-haiku-20240307",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
}
OPENAI_MODELS = {
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-32k",
}
GOOGLE_MODELS = {
    "gemini-1.5-pro-002",
    "gemini-2.5-pro",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
}
AZURE_OPENAI_MODELS = {
    "apex-demos-gpt-4-32k",
    "apex-demos-gpt-4o",
}
ALM_TOOL_TYPES = {"ADO", "Jira", "Custom"}

MODEL_OPTIONS = list(AZURE_OPENAI_MODELS.union(OPENAI_MODELS).union(ANTHROPIC_MODELS).union(GOOGLE_MODELS))

# --- Session History Store ---

_store: Dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    return InMemoryChatMessageHistory()

# --- Model Construction ---

def construct_model(llm_config: LLMModelConfig) -> BaseChatModel:
    llm_name = llm_config.name
    temperature = llm_config.temperature

    if llm_name in ANTHROPIC_MODELS:
        return ChatAnthropic(
            model_name=llm_name,
            temperature=temperature,
            max_tokens_to_sample=4096,
        )
    if llm_name in OPENAI_MODELS:
        return ChatOpenAI(
            model_name=llm_name,
            temperature=temperature,
        )
    if llm_name in GOOGLE_MODELS:
        return GoogleGenerativeAI(
            model=llm_name,
            temperature=temperature,
            max_output_tokens=8096,
            api_key=os.environ.get("GOOGLE_API_KEY"),
        )
    if llm_name in AZURE_OPENAI_MODELS:
        return AzureChatOpenAI(
            azure_deployment=llm_name,
            temperature=temperature,
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        )
    raise ValueError(f"Unknown model name: {llm_name}")

# --- LLM Chain Initialization ---

llm_settings = get_llm_settings("planningverse/settings.db")
DEFAULT_MODEL_NAME = llm_settings.get("LLM_MODEL_NAME", "apex-demos-gpt-4o")
DEFAULT_TEMPERATURE = float(llm_settings.get("LLM_MODEL_TEMPERATURE", 0.0))

llm_config = LLMModelConfig(model_name=DEFAULT_MODEL_NAME, temperature=DEFAULT_TEMPERATURE)
llm_model = construct_model(llm_config=llm_config)
chain = llm_model

# --- Inference with History ---

def invoke_with_history(prompt: str, session_id: str) -> str:
    print("Invoking with history for session:", session_id, get_session_history(session_id))
    response = chain.invoke(prompt)
    if isinstance(response, dict) and "content" in response:
        get_session_history(session_id).add_message(response["content"])
    else:
        get_session_history(session_id).add_message(response)
    return response
