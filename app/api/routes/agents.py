from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.agents.file_agent import csv_agent
from app.service.azure_service import azure_service
import os
import shutil

router = APIRouter()


class AnalyzeRequest(BaseModel):
    query: str


class AnalyzeResponse(BaseModel):
    status: str
    result: Any


# Rotas
@router.get("/test-connection")
async def test_azure_connection():
    """Testa a conexão com o Azure OpenAI"""
    return azure_service.test_connection()


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Faz upload de um arquivo CSV e o carrega no agente
    """
    # Validar se é um arquivo CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são permitidos")

    file_path = f"data/{file.filename}"

    try:
        # Criar diretório se não existir
        os.makedirs("data", exist_ok=True)

        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Carregar no agente
        result = csv_agent.load_csv(file_path)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_csv(request: AnalyzeRequest):
    """
    Analisa o CSV carregado usando linguagem natural

    Exemplos de queries:
    - "Quantas linhas tem o arquivo?"
    - "Quais são as colunas?"
    - "Mostre um resumo estatístico dos dados"
    - "Quais são os valores únicos da coluna X?"
    """
    result = csv_agent.analyze(request.query)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return AnalyzeResponse(
        status=result["status"],
        result=result["result"]
    )


@router.get("/dataframe-info")
async def get_dataframe_info():
    """Retorna informações detalhadas sobre o DataFrame carregado"""
    info = csv_agent.get_dataframe_info()

    if info["status"] == "error":
        raise HTTPException(status_code=400, detail=info["message"])

    return info