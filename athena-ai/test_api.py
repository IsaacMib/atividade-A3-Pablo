#!/usr/bin/env python3
"""
Script de teste rápido para FastAPI server
Testa health check e models info sem precisar carregar os modelos pesados
"""

import sys
import time
from pathlib import Path

# Adicionar pasta raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List

# ======================
# Pydantic Models Básicos
# ======================

class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: Dict[str, bool]
    timestamp: float

class ModelInfo(BaseModel):
    name: str
    version: str
    license: str
    source: str

class ModelInfoResponse(BaseModel):
    models: List[ModelInfo]

# ======================
# FastAPI App
# ======================

app = FastAPI(
    title="Athena AI API - Test Mode",
    description="API de teste para análise multimodal de autismo (modo simplificado)",
    version="1.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - Permitir requests do Django
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# Endpoints de Teste
# ======================

@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "message": "Athena AI API - Test Mode",
        "docs": "/docs",
        "health": "/health",
        "models_info": "/models/info",
    }

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check simplificado"""
    return HealthResponse(
        status="healthy",
        version="1.0.0-test",
        models_loaded={
            "video_pipeline": False,
            "audio_pipeline": False,
            "text_pipeline": False,
            "fusion_pipeline": False,
        },
        timestamp=time.time()
    )

@app.get("/models/info", response_model=ModelInfoResponse)
def get_models_info():
    """Informações dos modelos (sem carregar)"""
    models = [
        ModelInfo(
            name="MediaPipe Face Mesh",
            version="0.10.8",
            license="Apache 2.0",
            source="https://github.com/google/mediapipe"
        ),
        ModelInfo(
            name="Silero VAD",
            version="latest",
            license="MIT",
            source="https://github.com/snakers4/silero-vad"
        ),
        ModelInfo(
            name="Wav2Vec2 XLSR-53 PT-BR",
            version="facebook/wav2vec2-large-xlsr-53-portuguese",
            license="Apache 2.0",
            source="https://huggingface.co/facebook/wav2vec2-large-xlsr-53-portuguese"
        ),
        ModelInfo(
            name="BERTimbau",
            version="neuralmind/bert-base-portuguese-cased",
            license="MIT",
            source="https://github.com/neuralmind-ai/portuguese-bert"
        ),
        ModelInfo(
            name="Sentence-Transformers",
            version="paraphrase-multilingual-mpnet-base-v2",
            license="Apache 2.0",
            source="https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        ),
    ]
    return ModelInfoResponse(models=models)

# ======================
# Startup/Shutdown Events
# ======================

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🚀 Athena AI API - Test Mode Iniciando...")
    print("="*60)
    print("✓ FastAPI configurado")
    print("✓ CORS habilitado")
    print("⚠️ Modelos de IA NÃO carregados (modo teste)")
    print("\n📚 Documentação interativa:")
    print("   Swagger UI: http://localhost:8001/docs")
    print("   ReDoc: http://localhost:8001/redoc")
    print("\n🔍 Endpoints disponíveis:")
    print("   GET  /         - Root endpoint")
    print("   GET  /health   - Health check")
    print("   GET  /models/info - Informações dos modelos")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    print("\n" + "="*60)
    print("🛑 Athena AI API - Test Mode Finalizando...")
    print("="*60 + "\n")

# ======================
# Main
# ======================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🧪 Iniciando servidor de TESTE FastAPI")
    print("="*60)
    print("ℹ️  Este é um servidor simplificado para teste de conectividade")
    print("ℹ️  Os modelos de IA NÃO serão carregados neste modo")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False,
    )
