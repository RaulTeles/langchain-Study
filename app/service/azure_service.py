from langchain_openai import AzureChatOpenAI
from app.core.settings import settings
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """
    Serviço responsável por gerenciar a conexão com Azure OpenAI
    """
    _instance: Optional['AzureOpenAIService'] = None
    _llm: Optional[AzureChatOpenAI] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._llm is None:
            self._initialize_llm()

    def _initialize_llm(self):
        """Inicializa a conexão com Azure OpenAI"""
        try:
            logger.info(f"Inicializando Azure OpenAI...")
            logger.info(f"Endpoint: {settings.azure_openai_endpoint}")
            logger.info(f"Deployment: {settings.azure_openai_deployment_name}")
            logger.info(f"API Version: {settings.azure_openai_api_version}")

            self._llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                deployment_name=settings.azure_openai_deployment_name,
                api_version=settings.azure_openai_api_version,
                api_key=settings.azure_openai_api_key,
                temperature=0.7,
                max_tokens=4000
            )

            logger.info("✅ Serviço Azure OpenAI inicializado com sucesso!")

        except Exception as e:
            logger.error(f" Erro ao inicializar Azure OpenAI: {str(e)}")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            self._llm = None
            raise

    def get_llm(self) -> Optional[AzureChatOpenAI]:
        """Retorna a instância do LLM"""
        if self._llm is None:
            self._initialize_llm()
        return self._llm

try:
    azure_service = AzureOpenAIService()
except Exception as e:
    logger.error(f"Falha crítica ao criar serviço Azure: {str(e)}")
    azure_service = None