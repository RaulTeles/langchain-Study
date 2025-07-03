import pandas as pd
import logging
from functools import partial
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.service.azure_service import azure_service
from app.tools.custom_tools import save_json_to_file, get_usina_data_from_dataframe
from langchain.tools import Tool
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class UsinaDataToolArgs(BaseModel):
    usina_name: str


class FileAnalyzerAgent:
    def __init__(self):
        self.llm = azure_service.get_llm()
        self.file_path = None
        self.sheet_names = []
        self.df = None
        self.orchestrator_agent = None

    def load_file(self, file_path: str):
        self.file_path = file_path
        try:
            if file_path.endswith('.csv'):
                self.sheet_names = ['default']
            else:
                self.sheet_names = pd.ExcelFile(file_path).sheet_names
            return self.sheet_names
        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo: {e}")

    def setup_agents(self, sheet_name: str):
        if not self.file_path: raise ValueError("Nenhum arquivo foi carregado.")
        if sheet_name not in self.sheet_names: raise ValueError(f"Planilha '{sheet_name}' não encontrada.")

        try:
            logging.info(f"A carregar a planilha '{sheet_name}'...")
            self.df = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)
            self.df.columns = [f'col_{i}' for i in range(len(self.df.columns))]
            df_dict = self.df.to_dict(orient='list')
            logging.info("Planilha carregada e convertida para dicionário.")

            get_data_func = partial(get_usina_data_from_dataframe, df_dict=df_dict)

            usina_data_tool = Tool(
                name="get_usina_data",
                description="Use esta ferramenta para obter os dados detalhados de uma única usina. Você precisa passar o nome da usina (ex: 'USINA I').",
                func=get_data_func,
                args_schema=UsinaDataToolArgs
            )

            orchestrator_tools = [
                usina_data_tool,
                save_json_to_file
            ]

            system_prompt_text = """Você é um agente orquestrador de projetos, especialista em analisar dados de usinas. Sua função é receber pedidos do utilizador e usar as suas ferramentas para os executar.

            ### Ferramentas Disponíveis:
            - `get_usina_data`: Use esta ferramenta para obter os dados detalhados de uma única usina. Você precisa passar o nome da usina.
            - `save_json_to_file`: Salva um resultado JSON em um arquivo.

            ### Como Agir:
            1.  O utilizador vai pedir dados de uma ou mais usinas.
            2.  Para CADA usina pedida, você DEVE chamar a ferramenta `get_usina_data` com o nome da usina.
            3.  Se o utilizador pedir "todas as usinas", você deve chamar a ferramenta `get_usina_data` CINCO vezes, uma para cada usina: "USINA I", "USINA II", "USINA III", "USINA IV", "USINA V".
            4.  Compile os resultados de todas as chamadas em uma única resposta JSON.
            5.  Se o utilizador pedir para salvar, use a ferramenta `save_json_to_file` com o JSON compilado.
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt_text),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            orchestrator_agent_runnable = create_openai_functions_agent(self.llm, orchestrator_tools, prompt)

            self.orchestrator_agent = AgentExecutor(
                agent=orchestrator_agent_runnable,
                tools=orchestrator_tools,
                verbose=True,
                handle_parsing_errors=True
            )
            logging.info("Agente Orquestrador (versão Tool explícita) criado com sucesso.")
            return f"Agentes prontos para a planilha '{sheet_name}'."

        except Exception as e:
            logging.error(f"Falha ao configurar os agentes: {e}", exc_info=True)
            raise ValueError(f"Erro ao configurar os agentes: {e}")

    def run_main_agent(self, query: str) -> str:
        if not self.orchestrator_agent:
            raise ValueError("Os agentes não foram configurados...")
        try:
            response = self.orchestrator_agent.invoke({"input": query})
            return response.get("output", "O agente concluiu a tarefa sem uma resposta final explícita.")
        except Exception as e:
            return f"Ocorreu um erro durante a execução do agente: {e}"


file_agent = FileAnalyzerAgent()