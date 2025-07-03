from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.api.routes import agents

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router, prefix="/api/v1/agent", tags=["agent"])

@app.get("/")
async def root():
    return {
        "message": "API LangChain CSV Analyzer está funcionando!",
        "version": settings.app_version
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}