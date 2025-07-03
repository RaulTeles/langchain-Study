import json
import os
from langchain.tools import tool
from pydantic import BaseModel, Field


class SaveJsonArgs(BaseModel):
    filename: str
    json_data: str


@tool("save_json_to_file", args_schema=SaveJsonArgs)
def save_json_to_file(filename: str, json_data: str) -> str:
    """
    Salva uma string de conteúdo JSON num ficheiro dentro da pasta 'data'.
    Use esta ferramenta quando o utilizador pedir para guardar um resultado.
    """
    try:
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)

        if not filename.endswith('.json'):
            filename += '.json'

        file_path = os.path.join(data_dir, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_data)

        return f"Sucesso! O ficheiro foi salvo em: {file_path}"
    except Exception as e:
        return f"Erro ao salvar o ficheiro: {e}"