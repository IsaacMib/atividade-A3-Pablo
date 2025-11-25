"""
FastAPI Server - API de IA Multimodal para Triagem de Autismo

Endpoints:
- POST /analyze/text - Análise de texto
- POST /analyze/audio - Análise de áudio
- POST /analyze/video - Análise de vídeo
- POST /analyze/multimodal - Análise multimodal completa
- GET /health - Health check
- GET /models/info - Informações dos modelos

Autor: NEUROATHENA Team
Data: 2024-11-24
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn
from pathlib import Path
import tempfile
import logging

# Imports dos pipelines
import sys
sys.path.append(str(Path(__file__).parent.parent))

from video_model.pipeline import VideoPipeline, VideoAnalysisResult
from audio_model.pipeline import AudioPipeline, AudioAnalysisResult
from text_model.pipeline import TextPipeline, TextAnalysisResult
from multimodal_fusion.fusion_layer import (
    MultimodalFusionPipeline,
    MultimodalFeatures,
    FusionResult
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar app FastAPI
app = FastAPI(
    title="Athena AI API",
    description="API de IA Multimodal para Triagem Precoce de Autismo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Permitir requests do Django
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Modelos Pydantic para Request/Response
# ============================================================================

class TextAnalysisRequest(BaseModel):
    """Request para análise de texto."""
    text: str = Field(..., min_length=10, description="Texto para análise")


class AudioAnalysisResponse(BaseModel):
    """Response da análise de áudio."""
    score_audio: float
    prosody_atipica: bool
    prosody_score: float
    ritmo_irregular: bool
    pausas_longas: bool
    speech_rate: float
    emocao_predominante: str
    emocao_scores: Dict[str, float]
    alertas: List[str]
    duracao_segundos: float


class TextAnalysisResponse(BaseModel):
    """Response da análise de texto."""
    score_text: float
    sentiment: str
    sentiment_scores: Dict[str, float]
    concern_level: float
    concern_category: str
    symptoms_detected: List[str]
    symptom_severity: str
    alertas: List[str]


class VideoAnalysisResponse(BaseModel):
    """Response da análise de vídeo."""
    score_video: float
    contato_visual: Dict[str, float]
    expressoes: Dict[str, float]
    head_pose: Dict[str, float]
    gestos: Dict[str, bool]
    alertas: List[str]
    frames_analisados: int


class MultimodalAnalysisResponse(BaseModel):
    """Response da análise multimodal."""
    score_final: float
    nivel_risco: str
    confianca: float
    scores_modalidades: Dict[str, float]
    attention_weights: Dict[str, float]
    principais_indicadores: List[str]
    recomendacoes: List[str]


class HealthResponse(BaseModel):
    """Response do health check."""
    status: str
    version: str
    models_loaded: Dict[str, bool]


class ModelInfoResponse(BaseModel):
    """Informações dos modelos carregados."""
    video_model: Dict[str, str]
    audio_model: Dict[str, str]
    text_model: Dict[str, str]
    fusion_model: Dict[str, str]


# ============================================================================
# Inicialização dos Pipelines (Lazy Loading)
# ============================================================================

class PipelineManager:
    """Gerenciador de pipelines de IA."""
    
    def __init__(self):
        self._video_pipeline = None
        self._audio_pipeline = None
        self._text_pipeline = None
        self._fusion_pipeline = None
        
        self.models_loaded = {
            'video': False,
            'audio': False,
            'text': False,
            'fusion': False
        }
    
    @property
    def video_pipeline(self) -> VideoPipeline:
        """Lazy loading do pipeline de vídeo."""
        if self._video_pipeline is None:
            logger.info("Carregando Video Pipeline...")
            self._video_pipeline = VideoPipeline()
            self.models_loaded['video'] = True
            logger.info("Video Pipeline carregado com sucesso")
        return self._video_pipeline
    
    @property
    def audio_pipeline(self) -> AudioPipeline:
        """Lazy loading do pipeline de áudio."""
        if self._audio_pipeline is None:
            logger.info("Carregando Audio Pipeline...")
            self._audio_pipeline = AudioPipeline()
            self.models_loaded['audio'] = True
            logger.info("Audio Pipeline carregado com sucesso")
        return self._audio_pipeline
    
    @property
    def text_pipeline(self) -> TextPipeline:
        """Lazy loading do pipeline de texto."""
        if self._text_pipeline is None:
            logger.info("Carregando Text Pipeline...")
            self._text_pipeline = TextPipeline()
            self.models_loaded['text'] = True
            logger.info("Text Pipeline carregado com sucesso")
        return self._text_pipeline
    
    @property
    def fusion_pipeline(self) -> MultimodalFusionPipeline:
        """Lazy loading do pipeline de fusão."""
        if self._fusion_pipeline is None:
            logger.info("Carregando Fusion Pipeline...")
            self._fusion_pipeline = MultimodalFusionPipeline(
                fusion_method='transformer'
            )
            self.models_loaded['fusion'] = True
            logger.info("Fusion Pipeline carregado com sucesso")
        return self._fusion_pipeline


# Instância global do gerenciador
pipeline_manager = PipelineManager()


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Athena AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded=pipeline_manager.models_loaded
    )


@app.get("/models/info", response_model=ModelInfoResponse)
async def models_info():
    """Retorna informações dos modelos carregados."""
    return ModelInfoResponse(
        video_model={
            "name": "MediaPipe Face Mesh + Pose + Hands",
            "version": "0.10.8",
            "license": "Apache 2.0"
        },
        audio_model={
            "name": "Silero VAD + Wav2Vec2 XLSR-53 PT-BR",
            "version": "facebook/wav2vec2-large-xlsr-53-portuguese",
            "license": "MIT + Apache 2.0"
        },
        text_model={
            "name": "BERTimbau + Sentence-Transformers",
            "version": "neuralmind/bert-base-portuguese-cased",
            "license": "MIT + Apache 2.0"
        },
        fusion_model={
            "name": "Transformer Multimodal Fusion",
            "version": "1.0.0",
            "license": "Open-source"
        }
    )


@app.post("/analyze/text", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analisa texto (respostas de questionários, observações).
    
    Args:
        request: TextAnalysisRequest com texto
    
    Returns:
        TextAnalysisResponse com análise completa
    """
    try:
        logger.info(f"Análise de texto iniciada (len={len(request.text)})")
        
        # Análise
        result = pipeline_manager.text_pipeline.analyze_text(
            request.text,
            return_embeddings=False
        )
        
        logger.info(f"Análise de texto concluída: score={result.score_text:.2f}")
        
        return TextAnalysisResponse(
            score_text=result.score_text,
            sentiment=result.sentiment,
            sentiment_scores=result.sentiment_scores,
            concern_level=result.concern_level,
            concern_category=result.concern_category,
            symptoms_detected=result.symptoms_detected,
            symptom_severity=result.symptom_severity,
            alertas=result.alertas
        )
    
    except Exception as e:
        logger.error(f"Erro na análise de texto: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/audio", response_model=AudioAnalysisResponse)
async def analyze_audio(audio_file: UploadFile = File(...)):
    """
    Analisa arquivo de áudio (fala da criança).
    
    Args:
        audio_file: Arquivo de áudio (.wav, .mp3, .m4a)
    
    Returns:
        AudioAnalysisResponse com análise completa
    """
    try:
        logger.info(f"Análise de áudio iniciada: {audio_file.filename}")
        
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=Path(audio_file.filename).suffix
        ) as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Análise
        result = pipeline_manager.audio_pipeline.analyze_audio(
            tmp_path,
            return_embeddings=False
        )
        
        # Limpar arquivo temporário
        Path(tmp_path).unlink()
        
        logger.info(f"Análise de áudio concluída: score={result.score_audio:.2f}")
        
        return AudioAnalysisResponse(
            score_audio=result.score_audio,
            prosody_atipica=result.prosody_atipica,
            prosody_score=result.prosody_score,
            ritmo_irregular=result.ritmo_irregular,
            pausas_longas=result.pausas_longas,
            speech_rate=result.speech_rate,
            emocao_predominante=result.emocao_predominante,
            emocao_scores=result.emocao_scores,
            alertas=result.alertas,
            duracao_segundos=result.duracao_segundos
        )
    
    except Exception as e:
        logger.error(f"Erro na análise de áudio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/video", response_model=VideoAnalysisResponse)
async def analyze_video(video_file: UploadFile = File(...)):
    """
    Analisa arquivo de vídeo (interação da criança).
    
    Args:
        video_file: Arquivo de vídeo (.mp4, .avi, .mov)
    
    Returns:
        VideoAnalysisResponse com análise completa
    """
    try:
        logger.info(f"Análise de vídeo iniciada: {video_file.filename}")
        
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(video_file.filename).suffix
        ) as tmp_file:
            content = await video_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Análise
        result = pipeline_manager.video_pipeline.analyze_video(
            tmp_path,
            sample_rate=5,
            return_embeddings=False
        )
        
        # Limpar arquivo temporário
        Path(tmp_path).unlink()
        
        logger.info(f"Análise de vídeo concluída: score={result.score_video:.2f}")
        
        return VideoAnalysisResponse(
            score_video=result.score_video,
            contato_visual=result.contato_visual,
            expressoes=result.expressoes,
            head_pose=result.head_pose,
            gestos=result.gestos,
            alertas=result.alertas,
            frames_analisados=result.frames_analisados
        )
    
    except Exception as e:
        logger.error(f"Erro na análise de vídeo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/multimodal", response_model=MultimodalAnalysisResponse)
async def analyze_multimodal(
    text: Optional[str] = None,
    audio_file: Optional[UploadFile] = File(None),
    video_file: Optional[UploadFile] = File(None)
):
    """
    Análise multimodal completa combinando texto, áudio e vídeo.
    
    Args:
        text: Texto opcional
        audio_file: Arquivo de áudio opcional
        video_file: Arquivo de vídeo opcional
    
    Returns:
        MultimodalAnalysisResponse com fusão de todas modalidades
    """
    try:
        logger.info("Análise multimodal iniciada")
        
        # Verificar se pelo menos uma modalidade foi fornecida
        if not any([text, audio_file, video_file]):
            raise HTTPException(
                status_code=400,
                detail="Pelo menos uma modalidade deve ser fornecida"
            )
        
        # Features multimodais
        features = MultimodalFeatures(available_modalities=[])
        
        # Análise de texto
        if text:
            logger.info("Processando texto...")
            text_result = pipeline_manager.text_pipeline.analyze_text(text)
            features.text_embeddings = text_result.features.embeddings
            features.text_score = text_result.score_text
            features.available_modalities.append('text')
        
        # Análise de áudio
        if audio_file:
            logger.info(f"Processando áudio: {audio_file.filename}")
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(audio_file.filename).suffix
            ) as tmp_file:
                content = await audio_file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            audio_result = pipeline_manager.audio_pipeline.analyze_audio(tmp_path)
            features.audio_embeddings = audio_result.features.embeddings
            features.audio_score = audio_result.score_audio
            features.available_modalities.append('audio')
            
            Path(tmp_path).unlink()
        
        # Análise de vídeo
        if video_file:
            logger.info(f"Processando vídeo: {video_file.filename}")
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(video_file.filename).suffix
            ) as tmp_file:
                content = await video_file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            video_result = pipeline_manager.video_pipeline.analyze_video(tmp_path)
            features.video_embeddings = video_result.embeddings
            features.video_score = video_result.score_video
            features.available_modalities.append('video')
            
            Path(tmp_path).unlink()
        
        # Fusão multimodal
        logger.info("Executando fusão multimodal...")
        fusion_result = pipeline_manager.fusion_pipeline.fuse(
            features,
            return_embeddings=False
        )
        
        logger.info(
            f"Análise multimodal concluída: "
            f"score={fusion_result.score_final:.2f}, "
            f"risco={fusion_result.nivel_risco}"
        )
        
        return MultimodalAnalysisResponse(
            score_final=fusion_result.score_final,
            nivel_risco=fusion_result.nivel_risco,
            confianca=fusion_result.confianca,
            scores_modalidades=fusion_result.scores_modalidades,
            attention_weights=fusion_result.attention_weights,
            principais_indicadores=fusion_result.principais_indicadores,
            recomendacoes=fusion_result.recomendacoes
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise multimodal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Evento de inicialização."""
    logger.info("="*60)
    logger.info("Athena AI API - Iniciando...")
    logger.info("="*60)
    logger.info("Modelos serão carregados sob demanda (lazy loading)")
    logger.info("API pronta para receber requisições")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de finalização."""
    logger.info("Athena AI API - Finalizando...")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
