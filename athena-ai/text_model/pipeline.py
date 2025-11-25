"""
Pipeline de Análise de Texto para Triagem de Autismo

Analisa respostas textuais dos pais/responsáveis e notas clínicas:
- Padrões linguísticos associados a TEA
- Análise de sentimento e preocupação
- Detecção de sintomas mencionados
- Named Entity Recognition (NER) para identificar comportamentos

Open-Source Models:
1. BERTimbau (BERT PT-BR)
   - Repo: https://github.com/neuralmind-ai/portuguese-bert
   - Model: neuralmind/bert-base-portuguese-cased
   - License: MIT
   - Usage: Embeddings de texto e análise semântica

2. SpaCy PT-BR
   - Repo: https://github.com/explosion/spaCy
   - Model: pt_core_news_lg
   - License: MIT
   - Usage: NER, POS tagging, dependency parsing

3. Sentence-Transformers
   - Repo: https://github.com/UKPLab/sentence-transformers
   - Model: paraphrase-multilingual-mpnet-base-v2
   - License: Apache 2.0
   - Usage: Sentence embeddings para similaridade

Autor: NEUROATHENA Team
Data: 2024-11-24
"""

import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
import re


@dataclass
class TextFeatures:
    """Features extraídas do texto."""
    # Sentiment scores
    sentiment_positive: float
    sentiment_negative: float
    sentiment_neutral: float
    
    # Concern indicators
    concern_level: float  # 0-1, quanto maior mais preocupação
    
    # Symptom mentions
    symptom_keywords: List[str]  # Keywords TEA mencionadas
    symptom_count: int
    
    # Linguistic features
    text_length: int  # Número de palavras
    sentence_count: int
    avg_sentence_length: float
    
    # Embeddings
    embeddings: np.ndarray  # [768] - BERTimbau features
    sentence_embedding: np.ndarray  # [768] - Sentence-Transformer


@dataclass
class TextAnalysisResult:
    """Resultado da análise de texto."""
    score_text: float  # 0-1
    
    # Sentiment analysis
    sentiment: str  # positive, negative, neutral
    sentiment_scores: Dict[str, float]
    
    # Concern level
    concern_level: float
    concern_category: str  # baixa, média, alta
    
    # Symptom detection
    symptoms_detected: List[str]
    symptom_severity: str  # leve, moderado, severo
    
    # Features for multimodal fusion
    features: TextFeatures
    
    # Alerts
    alertas: List[str]
    
    # Metadata
    texto_original: str
    texto_processado: str


class BERTimbauSentimentAnalyzer:
    """Análise de sentimento usando BERTimbau."""
    
    def __init__(self, model_name: str = "neuralmind/bert-base-portuguese-cased"):
        """
        Inicializa BERTimbau para análise de sentimento.
        
        Model: neuralmind/bert-base-portuguese-cased
        - 110M parameters
        - Trained on BrWaC corpus (2.68B tokens)
        - Output: [seq_len, 768] hidden states
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        
        # Sentiment classifier (MLP simples em cima do BERTimbau)
        self.sentiment_classifier = nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 3)  # positive, negative, neutral
        )
        
        self.sentiment_labels = ['positive', 'negative', 'neutral']
    
    def analyze_sentiment(self, text: str) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Analisa sentimento do texto.
        
        Args:
            text: Texto em português
        
        Returns:
            embeddings: Tensor [768] - pooled CLS token
            sentiment_scores: Dict com scores por sentimento
        """
        # Tokenizar
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Extrair features
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Usar CLS token como representação do texto
            cls_embedding = outputs.last_hidden_state[:, 0, :]  # [1, 768]
            
            # Predizer sentimento
            sentiment_logits = self.sentiment_classifier(cls_embedding)  # [1, 3]
            sentiment_probs = torch.softmax(sentiment_logits, dim=-1)[0]
            
            sentiment_scores = {
                label: float(prob)
                for label, prob in zip(self.sentiment_labels, sentiment_probs)
            }
        
        return cls_embedding.squeeze(0), sentiment_scores
    
    def calculate_concern_level(self, text: str, sentiment_scores: Dict[str, float]) -> float:
        """
        Calcula nível de preocupação baseado em texto e sentimento.
        
        Concern indicators:
        - Palavras de preocupação: "preocupado", "ansioso", "medo", etc.
        - Negação: "não fala", "não olha", "não interage"
        - Sentimento negativo alto
        """
        text_lower = text.lower()
        
        # Keywords de preocupação
        concern_keywords = [
            'preocupado', 'preocupada', 'ansioso', 'ansiosa', 'medo', 'receio',
            'difícil', 'dificuldade', 'problema', 'demora', 'atraso',
            'não consegue', 'não fala', 'não olha', 'não interage', 'não brinca',
            'isolado', 'sozinho', 'repetitivo', 'estranho', 'diferente'
        ]
        
        concern_count = sum(1 for keyword in concern_keywords if keyword in text_lower)
        
        # Normalizar count (max 5 keywords = 0.5 de concern)
        concern_from_keywords = min(concern_count / 10, 0.5)
        
        # Concern do sentimento negativo
        concern_from_sentiment = sentiment_scores.get('negative', 0) * 0.5
        
        # Total concern (0-1)
        total_concern = concern_from_keywords + concern_from_sentiment
        
        return min(total_concern, 1.0)


class SymptomDetector:
    """Detecta sintomas de TEA mencionados no texto."""
    
    def __init__(self):
        """Inicializa detector de sintomas."""
        # Dicionário de sintomas TEA por categoria
        # Baseado em DSM-5 e literatura
        self.symptom_keywords = {
            # Comunicação social
            'comunicacao': [
                'não fala', 'não conversa', 'poucas palavras', 'vocabulário limitado',
                'ecolalia', 'repete palavras', 'não responde nome', 'não pede',
                'dificuldade comunicação', 'atraso fala', 'linguagem atrasada'
            ],
            
            # Interação social
            'interacao_social': [
                'não olha olhos', 'evita contato visual', 'não interage', 
                'prefere ficar sozinho', 'não brinca crianças', 'isolado',
                'não compartilha', 'dificuldade fazer amigos', 'solitário',
                'não aponta', 'não mostra objetos'
            ],
            
            # Comportamentos repetitivos
            'comportamento_repetitivo': [
                'movimentos repetitivos', 'balança corpo', 'bate mãos', 'flapping',
                'gira objetos', 'alinha brinquedos', 'rituais', 'rotinas rígidas',
                'interesses restritos', 'obsessão por', 'fixação em'
            ],
            
            # Processamento sensorial
            'sensorial': [
                'sensível sons', 'tampa ouvidos', 'não gosta toque', 'sensibilidade tátil',
                'seletivo comida', 'textura alimentos', 'hipersensível', 'hiposenível',
                'procura estímulos', 'gira corpo'
            ],
            
            # Regulação emocional
            'emocional': [
                'crises frequentes', 'birras intensas', 'choro inconsolável',
                'dificuldade transições', 'irritabilidade', 'ansiedade',
                'medo excessivo', 'agressividade'
            ]
        }
    
    def detect_symptoms(self, text: str) -> Tuple[List[str], int, Dict[str, int]]:
        """
        Detecta sintomas mencionados no texto.
        
        Returns:
            detected_symptoms: Lista de sintomas detectados
            total_count: Total de menções
            category_counts: Contagem por categoria
        """
        text_lower = text.lower()
        detected_symptoms = []
        category_counts = {}
        
        for category, keywords in self.symptom_keywords.items():
            count = 0
            for keyword in keywords:
                if keyword in text_lower:
                    detected_symptoms.append(keyword)
                    count += 1
            
            category_counts[category] = count
        
        return detected_symptoms, len(detected_symptoms), category_counts
    
    def classify_severity(self, symptom_count: int, category_counts: Dict[str, int]) -> str:
        """
        Classifica severidade baseada em número e distribuição de sintomas.
        
        Returns:
            'leve', 'moderado', 'severo'
        """
        # Número de categorias afetadas
        affected_categories = sum(1 for count in category_counts.values() if count > 0)
        
        # Severidade baseada em count e distribuição
        if symptom_count == 0:
            return 'nenhum'
        elif symptom_count <= 2 and affected_categories <= 1:
            return 'leve'
        elif symptom_count <= 5 and affected_categories <= 2:
            return 'moderado'
        else:
            return 'severo'


class SentenceEmbedder:
    """Cria sentence embeddings para similaridade semântica."""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        """
        Inicializa Sentence-Transformer multilingual.
        
        Model: paraphrase-multilingual-mpnet-base-v2
        - 278M parameters
        - Supports 50+ languages including PT-BR
        - Output: [768] sentence embedding
        """
        self.model = SentenceTransformer(model_name)
    
    def encode(self, text: str) -> np.ndarray:
        """
        Cria embedding de sentença.
        
        Args:
            text: Texto em português
        
        Returns:
            embedding: np.ndarray [768]
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding


class TextPreprocessor:
    """Preprocessamento de texto."""
    
    def __init__(self):
        """Inicializa preprocessador."""
        pass
    
    def clean_text(self, text: str) -> str:
        """Remove caracteres especiais e normaliza texto."""
        # Remover URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remover emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remover múltiplos espaços
        text = re.sub(r'\s+', ' ', text)
        
        # Remover espaços nas pontas
        text = text.strip()
        
        return text
    
    def extract_linguistic_features(self, text: str) -> Dict[str, float]:
        """Extrai features linguísticas básicas."""
        # Contar palavras
        words = text.split()
        word_count = len(words)
        
        # Contar sentenças (aproximado por pontuação)
        sentence_count = len(re.findall(r'[.!?]+', text))
        if sentence_count == 0:
            sentence_count = 1
        
        # Média de palavras por sentença
        avg_sentence_length = word_count / sentence_count
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': avg_sentence_length
        }


class TextPipeline:
    """Pipeline completo de análise de texto."""
    
    def __init__(self):
        """Inicializa pipeline de texto."""
        self.sentiment_analyzer = BERTimbauSentimentAnalyzer()
        self.symptom_detector = SymptomDetector()
        self.sentence_embedder = SentenceEmbedder()
        self.preprocessor = TextPreprocessor()
    
    def analyze_text(
        self,
        text: str,
        return_embeddings: bool = True
    ) -> TextAnalysisResult:
        """
        Analisa texto completo e retorna resultado.
        
        Args:
            text: Texto em português
            return_embeddings: Se deve retornar embeddings (para fusion)
        
        Returns:
            TextAnalysisResult com todas as métricas
        """
        # 1. Preprocessamento
        texto_original = text
        texto_processado = self.preprocessor.clean_text(text)
        
        if not texto_processado.strip():
            # Texto vazio
            return self._empty_result(texto_original)
        
        # 2. Features linguísticas
        ling_features = self.preprocessor.extract_linguistic_features(texto_processado)
        
        # 3. Análise de sentimento
        bert_embeddings, sentiment_scores = self.sentiment_analyzer.analyze_sentiment(texto_processado)
        sentiment = max(sentiment_scores, key=sentiment_scores.get)
        
        # 4. Nível de preocupação
        concern_level = self.sentiment_analyzer.calculate_concern_level(
            texto_processado, 
            sentiment_scores
        )
        concern_category = self._classify_concern(concern_level)
        
        # 5. Detecção de sintomas
        symptoms_detected, symptom_count, category_counts = self.symptom_detector.detect_symptoms(
            texto_processado
        )
        symptom_severity = self.symptom_detector.classify_severity(symptom_count, category_counts)
        
        # 6. Sentence embedding
        sentence_embedding = self.sentence_embedder.encode(texto_processado)
        
        # 7. Criar TextFeatures
        features = TextFeatures(
            sentiment_positive=sentiment_scores.get('positive', 0.0),
            sentiment_negative=sentiment_scores.get('negative', 0.0),
            sentiment_neutral=sentiment_scores.get('neutral', 0.0),
            concern_level=concern_level,
            symptom_keywords=symptoms_detected,
            symptom_count=symptom_count,
            text_length=ling_features['word_count'],
            sentence_count=ling_features['sentence_count'],
            avg_sentence_length=ling_features['avg_sentence_length'],
            embeddings=bert_embeddings.numpy() if return_embeddings else np.array([]),
            sentence_embedding=sentence_embedding if return_embeddings else np.array([])
        )
        
        # 8. Calcular score geral (0-1, 1 = baixo risco, 0 = alto risco)
        score_text = self._calculate_overall_score(
            concern_level,
            symptom_count,
            symptom_severity,
            sentiment_scores
        )
        
        # 9. Gerar alertas
        alertas = self._generate_alerts(
            concern_category,
            symptoms_detected,
            symptom_severity,
            sentiment
        )
        
        return TextAnalysisResult(
            score_text=score_text,
            sentiment=sentiment,
            sentiment_scores=sentiment_scores,
            concern_level=concern_level,
            concern_category=concern_category,
            symptoms_detected=symptoms_detected,
            symptom_severity=symptom_severity,
            features=features,
            alertas=alertas,
            texto_original=texto_original,
            texto_processado=texto_processado
        )
    
    def _empty_result(self, texto_original: str) -> TextAnalysisResult:
        """Retorna resultado vazio para texto vazio."""
        return TextAnalysisResult(
            score_text=0.5,  # Neutro
            sentiment='neutral',
            sentiment_scores={'positive': 0.0, 'negative': 0.0, 'neutral': 1.0},
            concern_level=0.0,
            concern_category='baixa',
            symptoms_detected=[],
            symptom_severity='nenhum',
            features=TextFeatures(
                sentiment_positive=0.0,
                sentiment_negative=0.0,
                sentiment_neutral=1.0,
                concern_level=0.0,
                symptom_keywords=[],
                symptom_count=0,
                text_length=0,
                sentence_count=0,
                avg_sentence_length=0.0,
                embeddings=np.array([]),
                sentence_embedding=np.array([])
            ),
            alertas=["Texto vazio ou muito curto para análise"],
            texto_original=texto_original,
            texto_processado=""
        )
    
    def _classify_concern(self, concern_level: float) -> str:
        """Classifica nível de preocupação em categoria."""
        if concern_level < 0.3:
            return 'baixa'
        elif concern_level < 0.6:
            return 'média'
        else:
            return 'alta'
    
    def _calculate_overall_score(
        self,
        concern_level: float,
        symptom_count: int,
        symptom_severity: str,
        sentiment_scores: Dict[str, float]
    ) -> float:
        """Calcula score geral de texto."""
        # Score inverso: quanto mais preocupação/sintomas, menor o score
        
        # Concern contribui negativamente
        score_concern = 1.0 - concern_level
        
        # Sintomas contribuem negativamente
        if symptom_severity == 'nenhum':
            score_symptoms = 1.0
        elif symptom_severity == 'leve':
            score_symptoms = 0.7
        elif symptom_severity == 'moderado':
            score_symptoms = 0.4
        else:  # severo
            score_symptoms = 0.1
        
        # Sentimento negativo contribui negativamente
        score_sentiment = 1.0 - sentiment_scores.get('negative', 0)
        
        # Média ponderada
        weights = [0.4, 0.4, 0.2]  # concern, symptoms, sentiment
        scores = [score_concern, score_symptoms, score_sentiment]
        
        return sum(w * s for w, s in zip(weights, scores))
    
    def _generate_alerts(
        self,
        concern_category: str,
        symptoms_detected: List[str],
        symptom_severity: str,
        sentiment: str
    ) -> List[str]:
        """Gera alertas baseados em indicadores."""
        alertas = []
        
        if concern_category == 'alta':
            alertas.append("Alto nível de preocupação detectado no texto")
        
        if symptom_severity == 'severo':
            alertas.append(f"Múltiplos sintomas de TEA mencionados ({len(symptoms_detected)} sintomas)")
        elif symptom_severity == 'moderado':
            alertas.append(f"Sintomas moderados de TEA mencionados ({len(symptoms_detected)} sintomas)")
        elif symptom_severity == 'leve':
            alertas.append(f"Poucos sintomas de TEA mencionados ({len(symptoms_detected)} sintomas)")
        
        if sentiment == 'negative':
            alertas.append("Sentimento predominantemente negativo no texto")
        
        # Listar categorias de sintomas mais comuns
        if symptoms_detected:
            # Agrupar por categoria (simplificado)
            categories_mentioned = set()
            for symptom in symptoms_detected:
                for cat, keywords in self.symptom_detector.symptom_keywords.items():
                    if symptom in keywords:
                        categories_mentioned.add(cat)
            
            if categories_mentioned:
                cat_names = {
                    'comunicacao': 'comunicação',
                    'interacao_social': 'interação social',
                    'comportamento_repetitivo': 'comportamentos repetitivos',
                    'sensorial': 'processamento sensorial',
                    'emocional': 'regulação emocional'
                }
                cat_str = ', '.join(cat_names.get(cat, cat) for cat in categories_mentioned)
                alertas.append(f"Áreas mencionadas: {cat_str}")
        
        if not alertas:
            alertas.append("Nenhum padrão atípico significativo detectado no texto")
        
        return alertas


# Exemplo de uso
if __name__ == "__main__":
    pipeline = TextPipeline()
    
    # Exemplo: análise de resposta de pai
    texto_exemplo = """
    Estou muito preocupada com meu filho. Ele tem 3 anos e ainda não fala,
    apenas repete algumas palavras que ouve na TV. Não olha nos olhos quando
    falo com ele e prefere ficar sozinho brincando sempre com os mesmos brinquedos,
    alinhando-os em fileiras. Quando tento mudar a rotina dele, ele tem crises
    intensas de choro. Também notei que ele tampa os ouvidos quando há barulho.
    """
    
    result = pipeline.analyze_text(texto_exemplo)
    
    print(f"Score Texto: {result.score_text:.2f}")
    print(f"Sentimento: {result.sentiment} ({result.sentiment_scores[result.sentiment]:.2f})")
    print(f"Nível de Preocupação: {result.concern_category} ({result.concern_level:.2f})")
    print(f"Sintomas Detectados: {len(result.symptoms_detected)}")
    print(f"Severidade: {result.symptom_severity}")
    print("\nAlertas:")
    for alerta in result.alertas:
        print(f"  - {alerta}")
