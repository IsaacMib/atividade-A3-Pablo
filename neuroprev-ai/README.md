# NeuroPrev AI - Sistema Multimodal de Triagem Precoce para TEA

## 📋 Visão Geral

Sistema de Inteligência Artificial multimodal para triagem precoce de Transtorno do Espectro Autista (TEA), combinando análise de **vídeo**, **áudio**, **texto** e **dados temporais** para gerar avaliações de risco precisas e explicáveis.

## 🏗️ Arquitetura do Sistema

```
neuroprev-ai/
├── video_model/          # Análise de expressões faciais, contato visual, gestos
│   ├── mediapipe/        # Google MediaPipe para detecção facial/pose/mãos
│   ├── insightface/      # InsightFace para análise facial avançada
│   ├── adapters/         # Adaptadores para normalização de embeddings
│   └── pipeline.py       # Pipeline de inferência de vídeo
│
├── audio_model/          # Análise de prosódia, ritmo, fluência, ecolalia
│   ├── silero/           # Silero VAD e diarização
│   ├── wav2vec2/         # Wav2Vec2 para features acústicas
│   ├── adapters/         # Adaptadores de áudio
│   └── pipeline.py       # Pipeline de inferência de áudio
│
├── text_model/           # NLP para respostas de pais e questionários
│   ├── transformers/     # HuggingFace Transformers (BERT, GPT)
│   ├── sentiment/        # Análise de sentimento
│   ├── adapters/         # Adaptadores de texto
│   └── pipeline.py       # Pipeline de inferência de texto
│
├── multimodal_fusion/    # Fusão de modalidades múltiplas
│   ├── clip/             # OpenAI CLIP para embedding multimodal
│   ├── imagebind/        # Meta ImageBind para 6 modalidades
│   ├── fusion_layer.py   # Camada de fusão (transformer/late fusion)
│   ├── classifier.py     # Classificador de risco TEA
│   └── explainer.py      # Módulo de explicabilidade (Grad-CAM, attention)
│
├── api/                  # API FastAPI
│   ├── main.py           # Servidor FastAPI + Uvicorn
│   ├── endpoints/        # Endpoints REST
│   │   ├── text.py       # /analyze/text
│   │   ├── video.py      # /analyze/video
│   │   ├── audio.py      # /analyze/audio
│   │   └── multimodal.py # /analyze/multimodal
│   ├── schemas.py        # Pydantic schemas
│   └── config.py         # Configurações
│
├── utils/                # Utilitários compartilhados
│   ├── preprocessing/    # Pré-processamento de dados
│   ├── feature_extraction/ # Extração de features
│   ├── normalization/    # Normalização de embeddings
│   └── logging/          # Logging estruturado
│
├── training/             # Scripts de treinamento e fine-tuning
│   ├── lora/             # LoRA (Low-Rank Adaptation)
│   ├── datasets/         # Preparação de datasets
│   └── train.py          # Script principal de treinamento
│
├── models/               # Modelos treinados e checkpoints
│   ├── checkpoints/      # Checkpoints salvos
│   └── configs/          # Configurações de modelos
│
├── tests/                # Testes unitários e de integração
│   ├── test_video.py
│   ├── test_audio.py
│   ├── test_text.py
│   └── test_multimodal.py
│
├── requirements.txt      # Dependências Python
├── Dockerfile           # Container Docker para deploy
└── docker-compose.yml   # Orquestração com PostgreSQL/Redis
```

## 🔬 Fluxo de Dados - Pipeline Multimodal

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTRADA DE DADOS                         │
├─────────────────────────────────────────────────────────────┤
│  • Texto: Respostas de questionários M-CHAT/CARS/ABC       │
│  • Vídeo: Gravações da criança (expressões, gestos)        │
│  • Áudio: Amostras de fala/vocalização                     │
│  • Temporal: Registros diários (painel)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              EXTRAÇÃO DE FEATURES POR MODALIDADE            │
├─────────────────────────────────────────────────────────────┤
│  VIDEO MODULE                                               │
│  ├─ MediaPipe: Face mesh (468 landmarks)                   │
│  ├─ InsightFace: Face embeddings (512-dim)                 │
│  ├─ Features: Contato visual, sorriso, head pose           │
│  └─ Output: [batch, 768] tensor                            │
│                                                             │
│  AUDIO MODULE                                               │
│  ├─ Silero VAD: Voice activity detection                   │
│  ├─ Wav2Vec2: Acoustic features (768-dim)                  │
│  ├─ Features: Prosódia, ritmo, pausas, ecolalia            │
│  └─ Output: [batch, 768] tensor                            │
│                                                             │
│  TEXT MODULE                                                │
│  ├─ BERT/BERTimbau: Embeddings contextuais PT-BR           │
│  ├─ Sentiment: Análise emocional das respostas             │
│  ├─ Features: Padrões linguísticos, preocupações           │
│  └─ Output: [batch, 768] tensor                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           NORMALIZAÇÃO E ALINHAMENTO DE EMBEDDINGS          │
├─────────────────────────────────────────────────────────────┤
│  • Projeção linear para dim comum: 512-d                   │
│  • Layer normalization                                      │
│  • Dropout (0.1) para regularização                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              FUSÃO MULTIMODAL (Transformer)                 │
├─────────────────────────────────────────────────────────────┤
│  ESTRATÉGIAS:                                               │
│  1. CLIP-based: Contrastive learning entre modalidades      │
│  2. ImageBind: Embedding unificado 6 modalidades            │
│  3. Late Fusion: Concatenação + MLP                         │
│  4. Cross-Attention: Transformer multimodal                 │
│                                                             │
│  Arquitetura:                                               │
│  ├─ Self-attention entre modalidades                       │
│  ├─ Cross-attention temporal (registros diários)            │
│  ├─ Positional encoding                                     │
│  └─ Output: [batch, 1536] tensor fusionado                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CLASSIFICAÇÃO E GERAÇÃO DE RESULTADO           │
├─────────────────────────────────────────────────────────────┤
│  CLASSIFICADOR MLP:                                         │
│  ├─ FC1: 1536 → 512 (ReLU + Dropout)                       │
│  ├─ FC2: 512 → 256 (ReLU + Dropout)                        │
│  ├─ FC3: 256 → 4 classes (baixo/moderado/alto/muito_alto)  │
│  └─ Sigmoid: Probabilidade de risco TEA [0-1]              │
│                                                             │
│  OUTPUT ESTRUTURADO:                                        │
│  {                                                          │
│    "probabilidade_tea": 0.78,                              │
│    "nivel_risco": "alto",                                  │
│    "confianca": "alta",                                    │
│    "scores": {                                             │
│      "video": 0.82,                                        │
│      "audio": 0.75,                                        │
│      "texto": 0.77                                         │
│    },                                                      │
│    "areas_risco": {                                        │
│      "comunicacao": 0.85,                                  │
│      "interacao_social": 0.73,                             │
│      "comportamentos_repetitivos": 0.68                    │
│    },                                                      │
│    "alertas": [                                            │
│      {                                                     │
│        "severidade": "critico",                            │
│        "tipo": "ausencia_contato_visual",                  │
│        "confianca": 0.91,                                  │
│        "timestamp": 32.5                                   │
│      }                                                     │
│    ],                                                      │
│    "recomendacoes": [...]                                  │
│  }                                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              EXPLICABILIDADE (XAI)                          │
├─────────────────────────────────────────────────────────────┤
│  • Grad-CAM: Heatmaps de atenção no vídeo                  │
│  • Attention Weights: Tokens importantes no texto          │
│  • SHAP Values: Contribuição de cada feature               │
│  • Visualizações: Gráficos temporais, dashboards           │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 Modelos Open-Source Utilizados

### 1. **Análise de Vídeo**

#### MediaPipe (Google)
- **Repositório**: https://github.com/google/mediapipe
- **Licença**: Apache 2.0
- **Uso**: Detecção de rosto (Face Mesh 468 landmarks), pose (33 pontos), mãos (21 pontos)
- **Features extraídas**:
  - Contato visual: direção do olhar (eye gaze)
  - Expressões faciais: sorriso, surpresa, tristeza
  - Movimento de cabeça: head pose (yaw, pitch, roll)
  - Gestos: movimentos de mãos e corpo

#### InsightFace
- **Repositório**: https://github.com/deepinsight/insightface
- **Licença**: MIT
- **Uso**: Face recognition, análise de atributos faciais
- **Features extraídas**:
  - Face embeddings (512-dim ArcFace)
  - Idade estimada, gênero
  - Qualidade facial (blur, iluminação)

### 2. **Análise de Áudio**

#### Silero Models
- **Repositório**: https://github.com/snakers4/silero-models
- **Licença**: MIT
- **Uso**: Voice Activity Detection (VAD), diarização de speaker
- **Features extraídas**:
  - Segmentos de fala vs silêncio
  - Prosódia: pitch, intensidade, ritmo
  - Pausas e hesitações

#### Wav2Vec2 (Meta/Facebook)
- **Repositório**: https://github.com/facebookresearch/fairseq/tree/main/examples/wav2vec
- **Licença**: MIT
- **Uso**: Extração de features acústicas contextuais
- **Features extraídas**:
  - Acoustic embeddings (768-dim)
  - Padrões de ecolalia (repetição)
  - Fluência e articulação

### 3. **Análise de Texto (NLP)**

#### HuggingFace Transformers
- **Repositório**: https://github.com/huggingface/transformers
- **Licença**: Apache 2.0
- **Modelos usados**:
  - **BERTimbau**: BERT pré-treinado em português brasileiro
  - **mBERT**: Multilingual BERT
  - **GPT-2 Portuguese**: Geração de recomendações
- **Features extraídas**:
  - Sentiment analysis (positivo/negativo/neutro)
  - Named Entity Recognition (preocupações dos pais)
  - Padrões linguísticos (negação, dúvida, certeza)

### 4. **Fusão Multimodal**

#### CLIP (OpenAI)
- **Repositório**: https://github.com/openai/CLIP
- **Licença**: MIT
- **Uso**: Alinhamento entre visão e linguagem
- **Aplicação**: Correlacionar descrições dos pais com vídeos da criança

#### ImageBind (Meta)
- **Repositório**: https://github.com/facebookresearch/ImageBind
- **Licença**: MIT (CC BY-NC 4.0 para modelo)
- **Uso**: Embedding unificado para 6 modalidades (imagem, texto, áudio, vídeo, thermal, IMU)
- **Aplicação**: Fusão nativa de video + audio + texto em espaço latente comum

## 🚀 Endpoints da API

### FastAPI Server (http://localhost:8001)

```python
# 1. Análise de Texto
POST /analyze/text
Body: {
  "texto": "Meu filho não responde quando chamo pelo nome...",
  "tipo_questionario": "mchat",
  "respostas": [...]
}
Response: {
  "score_texto": 0.75,
  "sentimento": "preocupado",
  "keywords": ["não responde", "nome", "olhar"],
  "probabilidade_risco": 0.68
}

# 2. Análise de Vídeo
POST /analyze/video
Body: multipart/form-data
  - file: video.mp4
  - duracao_segundos: 120
Response: {
  "score_video": 0.82,
  "contato_visual": {
    "frequencia": 0.23,  # 23% do tempo
    "duracao_media": 1.2  # segundos
  },
  "expressoes": {
    "sorriso": 0.15,
    "surpresa": 0.05
  },
  "alertas": [
    {
      "tipo": "ausencia_contato_visual",
      "timestamp": 32.5,
      "confianca": 0.91,
      "frame_url": "/frames/video_123_frame_975.jpg"
    }
  ]
}

# 3. Análise de Áudio
POST /analyze/audio
Body: multipart/form-data
  - file: audio.wav
  - duracao_segundos: 60
Response: {
  "score_audio": 0.71,
  "vad": {
    "speech_ratio": 0.45,
    "pausas_longas": 12
  },
  "prosodia": {
    "pitch_mean": 250.5,
    "pitch_std": 45.2,
    "ritmo": "irregular"
  },
  "ecolalia_detectada": true
}

# 4. Análise Multimodal Completa
POST /analyze/multimodal
Body: multipart/form-data
  - texto: "..."
  - video: video.mp4
  - audio: audio.wav
  - dados_temporais: JSON com registros diários
Response: {
  "triagem_id": 123,
  "probabilidade_tea": 0.78,
  "nivel_risco": "alto",
  "confianca": "alta",
  "scores": {
    "video": 0.82,
    "audio": 0.75,
    "texto": 0.77,
    "temporal": 0.74
  },
  "areas_risco": {
    "comunicacao": 0.85,
    "interacao_social": 0.73,
    "comportamentos_repetitivos": 0.68
  },
  "alertas": [...],
  "recomendacoes": [
    "Encaminhar para avaliação com neuropediatra",
    "Considerar terapia ABA precoce",
    "Monitorar desenvolvimento da linguagem"
  ],
  "explicabilidade": {
    "grad_cam_video": "/explanations/gradcam_123.jpg",
    "attention_texto": {...},
    "shap_values": {...}
  }
}
```

## 🔧 Integração com Django

```python
# triagem_ia/services/ai_service.py

import requests
from django.conf import settings

class AIAnalysisService:
    """
    Serviço para comunicação com API FastAPI de IA.
    """
    API_BASE_URL = settings.NEUROPREV_AI_URL  # http://localhost:8001
    
    def analyze_multimodal(self, triagem_id, video_path=None, audio_path=None, texto=None):
        """
        Envia dados multimodais para análise.
        """
        files = {}
        if video_path:
            files['video'] = open(video_path, 'rb')
        if audio_path:
            files['audio'] = open(audio_path, 'rb')
        
        data = {
            'triagem_id': triagem_id,
            'texto': texto or ""
        }
        
        response = requests.post(
            f"{self.API_BASE_URL}/analyze/multimodal",
            files=files,
            data=data,
            timeout=300  # 5 minutos para processar
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro na análise: {response.text}")
    
    def save_result(self, triagem, result_data):
        """
        Salva resultado da IA no banco Django.
        """
        from triagem_ia.models import ResultadoIA, AlertaIA
        
        resultado = ResultadoIA.objects.create(
            triagem=triagem,
            probabilidade_tea=result_data['probabilidade_tea'],
            confianca=result_data['confianca'],
            score_texto=result_data['scores'].get('texto'),
            score_audio=result_data['scores'].get('audio'),
            score_video=result_data['scores'].get('video'),
            areas_risco=result_data['areas_risco'],
            modelo_utilizado="NeuroPrevMultimodal",
            versao_modelo="1.0.0"
        )
        
        # Criar alertas
        for alerta_data in result_data.get('alertas', []):
            AlertaIA.objects.create(
                resultado_ia=resultado,
                tipo_alerta=alerta_data['tipo'],
                severidade=alerta_data['severidade'],
                descricao=alerta_data.get('descricao', ''),
                modalidade_origem=alerta_data.get('modalidade', 'video'),
                timestamp_deteccao=alerta_data.get('timestamp'),
                confianca_deteccao=alerta_data['confianca']
            )
        
        return resultado
```

## 📦 Dependências Principais

```txt
# requirements.txt

# Deep Learning Core
torch==2.1.0
torchvision==0.16.0
torchaudio==2.1.0

# Computer Vision
mediapipe==0.10.8
insightface==0.7.3
opencv-python==4.8.1.78
onnxruntime==1.16.3

# Audio Processing
librosa==0.10.1
soundfile==0.12.1
pydub==0.25.1
pyannote.audio==3.1.1

# NLP
transformers==4.35.2
sentence-transformers==2.2.2
spacy==3.7.2

# Multimodal
open_clip_torch==2.23.0
timm==0.9.12

# API
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0

# ML Utilities
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.1.3

# Explicabilidade
shap==0.44.0
captum==0.7.0

# Fine-tuning
peft==0.7.0  # LoRA
bitsandbytes==0.41.3

# Utils
pillow==10.1.0
tqdm==4.66.1
python-dotenv==1.0.0
```

## 🎯 Roadmap de Implementação

### Fase 1: Infraestrutura Base ✅
- [x] Estrutura de pastas
- [x] Documentação de arquitetura
- [ ] Requirements.txt completo
- [ ] Docker + docker-compose

### Fase 2: Módulos Individuais
- [ ] Video Model Pipeline
- [ ] Audio Model Pipeline
- [ ] Text Model Pipeline
- [ ] Testes unitários por módulo

### Fase 3: Fusão Multimodal
- [ ] CLIP integration
- [ ] ImageBind integration
- [ ] Transformer fusion layer
- [ ] Classificador MLP

### Fase 4: API e Deploy
- [ ] FastAPI endpoints
- [ ] Integração com Django
- [ ] Celery para processamento assíncrono
- [ ] Docker deployment

### Fase 5: Explicabilidade e Fine-tuning
- [ ] Grad-CAM para vídeos
- [ ] Attention visualization
- [ ] LoRA fine-tuning
- [ ] Dashboard de explicações

## 📚 Referências Científicas

1. **Autism Screening**:
   - Thabtah, F. (2019). "Machine learning in autistic spectrum disorder behavioral research"
   - Hyde, K. K. et al. (2019). "Applications of supervised machine learning in autism spectrum disorder research"

2. **Multimodal Learning**:
   - Baltrusaitis, T. et al. (2019). "Multimodal Machine Learning: A Survey and Taxonomy"
   - Radford, A. et al. (2021). "Learning Transferable Visual Models From Natural Language Supervision" (CLIP)

3. **Early Detection**:
   - Pierce, K. et al. (2019). "Detecting, Studying, and Treating Autism Early: The One-Year Well-Baby Check-Up Approach"
   - Duda, M. et al. (2016). "Use of machine learning for behavioral distinction of autism and ADHD"

## 📄 Licença

Este projeto utiliza múltiplos modelos open-source com licenças variadas (MIT, Apache 2.0, CC BY-NC). 
Consulte cada submódulo para detalhes específicos de licenciamento.

**Importante**: Este sistema é uma **ferramenta de apoio** e NÃO substitui avaliação clínica profissional. 
Resultados devem ser interpretados por equipe médica especializada.
