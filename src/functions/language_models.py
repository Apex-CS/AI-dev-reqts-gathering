from langchain_openai import AzureChatOpenAI
import os

def construct_model(model_name, temperature):
    return AzureChatOpenAI(
        azure_deployment=model_name,
        temperature=temperature,
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
    )
