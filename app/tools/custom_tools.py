import json
import os
import pandas as pd
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Dict, Any, List


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


class GetUsinaDataArgs(BaseModel):
    usina_name: str = Field(description="O nome exato da usina para extrair os dados, por exemplo, 'USINA I'.")
    df_dict: Dict[str, List[Any]] = Field(description="O dataframe da planilha, convertido para um dicionário.")


def get_usina_data_from_dataframe(usina_name: str, df_dict: Dict[str, List[Any]]) -> str:
    """
    Extrai dados de uma usina específica de um dataframe.
    Esta é uma função interna e não deve ser exposta diretamente como uma ferramenta.
    O dataframe é recebido como um dicionário.
    A função retorna os dados da usina como uma string JSON.
    """
    df = pd.DataFrame.from_dict(df_dict)

    usinas_map = {
        "USINA I": {"hora": "col_1", "qtde": "col_2", "just": "col_3"},
        "USINA II": {"hora": "col_5", "qtde": "col_6", "just": "col_7"},
        "USINA III": {"hora": "col_9", "qtde": "col_10", "just": "col_11"},
        "USINA IV": {"hora": "col_13", "qtde": "col_14", "just": "col_15"},
        "USINA V": {"hora": "col_17", "qtde": "col_18", "just": "col_19"},
    }

    if usina_name.upper() not in usinas_map:
        return f"Erro: Usina '{usina_name}' não encontrada no mapa de dados."

    config = usinas_map[usina_name.upper()]

    try:
        usina_df = df[[config["hora"], config["qtde"], config["just"]]].copy()
        usina_df = usina_df.iloc[2:26]
        usina_df.columns = ["hora", "quantidade", "justificativa"]
        usina_df["quantidade"] = pd.to_numeric(usina_df["quantidade"], errors='coerce')
        usina_df["quantidade"] = usina_df["quantidade"].fillna(0).astype(int)
        usina_df["hora"] = usina_df["hora"].astype(str)
        usina_df["justificativa"] = usina_df["justificativa"].fillna("").astype(str)
        total_produzido = usina_df["quantidade"].sum()
        resultado = {
            "usina": usina_name.upper(),
            "total_produzido": int(total_produzido),
            "eventos": usina_df.to_dict(orient='records')
        }
        return json.dumps(resultado, ensure_ascii=False, indent=4)
    except KeyError as e:
        return f"Erro: A coluna {e} não foi encontrada no dataframe para a usina {usina_name}."
    except Exception as e:
        return f"Erro inesperado ao processar dados para {usina_name}: {str(e)}"