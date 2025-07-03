from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas do arquivo .env
    """
    azure_openai_api_key: str = Field(..., env='AZURE_OPENAI_API_KEY')
    azure_openai_endpoint: str = Field(..., env='AZURE_OPENAI_ENDPOINT')
    azure_openai_deployment_name: str = Field(..., env='AZURE_OPENAI_DEPLOYMENT_NAME')
    azure_openai_api_version: str = Field(default="2023-12-01-preview", env='AZURE_OPENAI_API_VERSION')

    app_name: str = Field(default="LangChain CSV Analyzer", env='APP_NAME')
    app_version: str = Field(default="1.0.0", env='APP_VERSION')
    debug: bool = Field(default=False, env='DEBUG')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


settings = Settings()