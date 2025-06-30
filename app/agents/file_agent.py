from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from app.service.azure_service import azure_service
import pandas as pd
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CSVAnalyzerAgent:
    """
    Agente especializado em analisar arquivos usando LangChain
    """

    def __init__(self):
        self.llm = azure_service.get_llm()
        self.df: Optional[pd.DataFrame] = None
        self.agent = None

    def load_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Carrega um arquivo CSV e cria o agente

        Args:
            file_path: Caminho para o arquivo CSV

        Returns:
            Dict com status e informações do arquivo
        """
        try:
            # Carregar o CSV
            self.df = pd.read_csv(file_path)

            self.agent = create_pandas_dataframe_agent(
                llm=self.llm,
                df=self.df,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                handle_parsing_errors=True,
                allow_dangerous_code=True
            )

            # Informações básicas sobre o arquivo
            info = {
                "status": "success",
                "rows": len(self.df),
                "columns": len(self.df.columns),
                "column_names": list(self.df.columns),
                "preview": self.df.head().to_dict()
            }

            logger.info(f"CSV carregado com sucesso: {info['rows']} linhas, {info['columns']} colunas")
            return info

        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao carregar arquivo: {str(e)}"
            }

    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Executa uma análise no DataFrame usando linguagem natural

        Args:
            query: Pergunta ou comando em linguagem natural

        Returns:
            Dict com o resultado da análise
        """
        if self.agent is None:
            return {
                "status": "error",
                "message": "Nenhum arquivo CSV foi carregado ainda"
            }

        try:
            # Executar a query no agente
            result = self.agent.run(query)

            return {
                "status": "success",
                "query": query,
                "result": result
            }

        except Exception as e:
            logger.error(f"Erro ao analisar: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro na análise: {str(e)}"
            }

    def get_dataframe_info(self) -> Dict[str, Any]:
        """Retorna informações detalhadas sobre o DataFrame atual"""
        if self.df is None:
            return {"status": "error", "message": "Nenhum DataFrame carregado"}

        try:
            # Converter dtypes para string para serialização JSON
            dtypes_dict = {}
            for col, dtype in self.df.dtypes.items():
                dtypes_dict[col] = str(dtype)

            # Converter describe() de forma segura
            description = {}
            describe_df = self.df.describe(include='all')
            for col in describe_df.columns:
                description[col] = {}
                for idx in describe_df.index:
                    value = describe_df.loc[idx, col]
                    # Converter valores numpy para Python nativo
                    if pd.notna(value):
                        if hasattr(value, 'item'):
                            description[col][idx] = value.item()
                        else:
                            description[col][idx] = str(value)
                    else:
                        description[col][idx] = None

            return {
                "status": "success",
                "shape": {
                    "rows": self.df.shape[0],
                    "columns": self.df.shape[1]
                },
                "columns": list(self.df.columns),
                "dtypes": dtypes_dict,
                "null_counts": self.df.isnull().sum().to_dict(),
                "description": description,
                "memory_usage": self.df.memory_usage().to_dict()
            }

        except Exception as e:
            logger.error(f"Erro ao obter informações do DataFrame: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao processar informações: {str(e)}"
            }


# Instância do agente
csv_agent = CSVAnalyzerAgent()