# app/agents/file_agent.py (Refatorado)

import pandas as pd
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from app.service.azure_service import azure_service


class FileAnalyzerAgent:
    """
    Um agente capaz de analisar arquivos de dados como CSV e vários formatos Excel.
    A lógica agora separa o upload do arquivo da análise da planilha.
    """

    def __init__(self):
        self.llm = azure_service.get_llm()
        self.file_path = None
        self.sheet_names = []
        self.df = None
        self.agent = None

    def load_file(self, file_path: str):
        """
        Carrega um arquivo, identifica o tipo e extrai os nomes das planilhas.
        Não carrega os dados completos para economizar memória.
        """
        self.file_path = file_path
        try:
            if file_path.endswith('.csv'):
                self.sheet_names = ['default']
            else:
                # Para arquivos Excel, usa ExcelFile para listar as planilhas sem carregar tudo
                xls = pd.ExcelFile(file_path, engine=self._get_engine(file_path))
                self.sheet_names = xls.sheet_names
            return self.sheet_names
        except Exception as e:
            # Em caso de erro (arquivo corrompido, formato inválido), reseta o estado
            self.file_path = None
            self.sheet_names = []
            raise ValueError(f"Erro ao ler o arquivo: {e}")

    def select_sheet_and_create_agent(self, sheet_name: str):
        """
        Carrega os dados de uma planilha específica em um DataFrame do Pandas
        e cria o agente LangChain para análise.
        """
        if not self.file_path:
            raise ValueError("Nenhum arquivo foi carregado. Faça o upload primeiro.")

        if sheet_name not in self.sheet_names:
            raise ValueError(f"Planilha '{sheet_name}' não encontrada no arquivo.")

        try:
            if self.file_path.endswith('.csv'):
                self.df = pd.read_csv(self.file_path)
            else:
                self.df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine=self._get_engine(self.file_path))

            # Cria o agente com o DataFrame recém-carregado
            self.agent = create_pandas_dataframe_agent(
                self.llm,
                self.df,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True  # Cuidado com esta opção em produção
            )
            return f"Planilha '{sheet_name}' carregada com sucesso e pronta para análise."
        except Exception as e:
            self.df = None
            self.agent = None
            raise ValueError(f"Erro ao carregar os dados da planilha '{sheet_name}': {e}")

    def analyze(self, query: str) -> str:
        """
        Executa uma consulta de linguagem natural usando o agente na planilha carregada.
        """
        if not self.agent or self.df is None:
            raise ValueError("Nenhuma planilha selecionada para análise. Use a função de carregar planilha primeiro.")

        try:
            response = self.agent.run(query)
            return response
        except Exception as e:
            return f"Ocorreu um erro durante a análise: {e}"

    def get_dataframe_info(self) -> dict:
        """
        Retorna informações sobre o DataFrame da planilha atualmente carregada.
        """
        if self.df is None:
            return {"error": "Nenhuma planilha está carregada."}

        return {
            "file_path": self.file_path,
            "sheet_name": self.df.attrs.get('sheet_name', 'default'),  # Guardando o nome da planilha
            "num_rows": self.df.shape[0],
            "num_cols": self.df.shape[1],
            "columns": self.df.columns.tolist(),
            "data_types": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "description": self.df.describe(include='all').to_dict()
        }

    def _get_engine(self, file_path: str):
        """Função auxiliar para determinar o motor de leitura do pandas."""
        if file_path.endswith('.xlsx') or file_path.endswith('.xlsm'):
            return 'openpyxl'
        if file_path.endswith('.xlsb'):
            return 'pyxlsb'
        if file_path.endswith('.xls'):
            return 'xlrd'
        return None


# Instância única do nosso agente (padrão Singleton)
file_agent = FileAnalyzerAgent()