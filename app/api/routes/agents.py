from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from app.agents.file_agent import file_agent
from app.service.azure_service import azure_service
import os
import re

router = APIRouter()

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.xlsb', '.xlsm'}


class AnalysisRequest(BaseModel):
    sheet_name: str
    query: str

class AnalysisResponse(BaseModel):
    response: str


class SheetListResponse(BaseModel):
    sheets: List[str]

def secure_filename(filename: str) -> str:

    filename = filename.replace(' ', '-')
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    filename = filename.lstrip('._-')
    return filename


@router.post("/upload-file", summary="Faz upload de um arquivo de dados (CSV ou Excel)")
def upload_file(file: UploadFile = File(...)):
    original_filename, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400,
                            detail=f"Tipo de arquivo não suportado. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}")

    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    safe_basename = secure_filename(original_filename)
    safe_filename = f"{safe_basename}{file_extension}"

    file_path = os.path.join(data_dir, safe_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    try:
        sheets = file_agent.load_file(file_path)
        return {"message": "Arquivo carregado com sucesso.", "file_name": safe_filename, "available_sheets": sheets}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sheets", response_model=SheetListResponse, summary="Lista as planilhas do arquivo carregado")
def get_sheets():
    if not file_agent.file_path:
        raise HTTPException(status_code=404, detail="Nenhum arquivo foi carregado ainda.")
    return {"sheets": file_agent.sheet_names}


@router.post("/analyze", response_model=AnalysisResponse, summary="Analisa uma planilha específica do arquivo")
def analyze(request: AnalysisRequest):
    try:
        file_agent.select_sheet_and_create_agent(request.sheet_name)

        response = file_agent.analyze(request.query)
        return {"response": response}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")


@router.get("/dataframe-info", summary="Obtém informações sobre a planilha atualmente carregada")
def get_dataframe_info():
    if not file_agent.agent:
        raise HTTPException(status_code=400, detail="Nenhuma planilha foi selecionada para análise.")
    info = file_agent.get_dataframe_info()
    return info


@router.get("/test-connection", summary="Testa a conexão com o serviço da Azure OpenAI")
def test_connection():
    try:
        return azure_service.test_connection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))