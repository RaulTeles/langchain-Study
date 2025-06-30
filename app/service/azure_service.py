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
        """Inicializa o serviço com as configurações do Azure"""
        if self._llm is None:
            self._initialize_llm()

    def _initialize_llm(self):
        """Inicializa a conexão com Azure OpenAI"""
        try:
            # Log das configurações (sem mostrar a API key completa)
            logger.info(f"Inicializando Azure OpenAI...")
            logger.info(f"Endpoint: {settings.azure_openai_endpoint}")
            logger.info(f"Deployment: {settings.azure_openai_deployment_name}")
            logger.info(f"API Version: {settings.azure_openai_api_version}")

            # Criar a instância do Azure Chat OpenAI
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
            logger.error(f"❌ Erro ao inicializar Azure OpenAI: {str(e)}")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            self._llm = None
            raise

    def get_llm(self) -> Optional[AzureChatOpenAI]:
        """Retorna a instância do LLM"""
        if self._llm is None:
            self._initialize_llm()
        return self._llm

    def test_connection(self):
        """Testa a conexão com o Azure OpenAI"""
        try:
            if self._llm is None:
                return {
                    "status": "error",
                    "message": "LLM não foi inicializado corretamente"
                }

            logger.info("Testando conexão com Azure OpenAI...")

            # Teste simples
            messages = [{"role": "user", "content": "Olá, teste de conexão!"}]
            response = self._llm.invoke(messages)

            logger.info("✅ Conexão bem-sucedida!")

            return {
                "status": "connected",
                "message": "Conexão com Azure OpenAI funcionando!",
                "response": response.content if hasattr(response, 'content') else str(response)
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Erro na conexão: {error_msg}")

            # Mensagens de erro mais específicas
            if "api_key" in error_msg.lower():
                return {
                    "status": "error",
                    "message": "Erro de autenticação: Verifique sua API Key",
                    "details": error_msg
                }
            elif "endpoint" in error_msg.lower():
                return {
                    "status": "error",
                    "message": "Erro de endpoint: Verifique a URL do Azure",
                    "details": error_msg
                }
            elif "deployment" in error_msg.lower():
                return {
                    "status": "error",
                    "message": "Erro de deployment: Verifique o nome do deployment",
                    "details": error_msg
                }
            else:
                return {
                    "status": "error",
                    "message": f"Erro na conexão: {error_msg}",
                    "error_type": type(e).__name__,
                    "details": error_msg
                }


# Criar instância do serviço
try:
    azure_service = AzureOpenAIService()
except Exception as e:
    logger.error(f"Falha crítica ao criar serviço Azure: {str(e)}")
    azure_service = None