import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

print("=== Testando configurações ===")
print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
print(f"Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
print(f"API Version: {os.getenv('AZURE_OPENAI_API_VERSION')}")
print(f"API Key exists: {bool(os.getenv('AZURE_OPENAI_API_KEY'))}")

print("\n=== Testando conexão direta ===")
try:
    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": "Teste"}],
        max_tokens=10
    )

    print("✅ Conexão direta funcionando!")
    print(f"Resposta: {response.choices[0].message.content}")

except Exception as e:
    print(f"❌ Erro: {str(e)}")