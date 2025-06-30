from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.api.routes import agents  # Mudança aqui!

# Criar instância do FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(agents.router, prefix="/api/v1/agent", tags=["agent"])
app.include_router

@app.get("/")
async def root():
    """Rota principal - Health Check"""
    return {
        "message": "API LangChain CSV Analyzer está funcionando!",
        "version": settings.app_version
    }

@app.get("/health")
async def health_check():
    """Verifica se a API está saudável"""
    return {"status": "healthy"}