"""
Fusion Layer Multimodal para Triagem de Autismo

Combina embeddings de vídeo, áudio e texto usando:
- Early fusion: Concatenação de features
- Late fusion: Ensemble de predições
- Attention-based fusion: Transformer multimodal
- Cross-modal alignment: CLIP/ImageBind

Open-Source Models:
1. CLIP (OpenAI)
   - Repo: https://github.com/openai/CLIP
   - License: MIT
   - Usage: Alinhamento visão-linguagem

2. ImageBind (Meta)
   - Repo: https://github.com/facebookresearch/ImageBind
   - License: CC BY-NC 4.0
   - Usage: 6 modalidades (image, video, audio, text, depth, IMU)

3. Transformer Fusion (Custom)
   - Architecture: Multi-head attention entre modalidades
   - License: Open-source (própria)
   - Usage: Fusão adaptativa com attention weights

Autor: NeuroPrev Team
Data: 2024-11-24
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path


@dataclass
class MultimodalFeatures:
    """Features de todas as modalidades."""
    # Video features
    video_embeddings: Optional[np.ndarray] = None  # [768]
    video_score: Optional[float] = None
    
    # Audio features
    audio_embeddings: Optional[np.ndarray] = None  # [512]
    audio_score: Optional[float] = None
    
    # Text features
    text_embeddings: Optional[np.ndarray] = None  # [768]
    text_sentence_embeddings: Optional[np.ndarray] = None  # [768]
    text_score: Optional[float] = None
    
    # Metadata
    available_modalities: List[str] = None  # ['video', 'audio', 'text']


@dataclass
class FusionResult:
    """Resultado da fusão multimodal."""
    # Classificação final
    score_final: float  # 0-1 (probabilidade de TEA)
    nivel_risco: str  # baixo, medio, alto
    confianca: float  # 0-1 (confiança na predição)
    
    # Scores por modalidade
    scores_modalidades: Dict[str, float]
    
    # Attention weights
    attention_weights: Dict[str, float]  # Importância de cada modalidade
    
    # Embeddings fusionados
    fused_embeddings: np.ndarray  # [1024]
    
    # Explicação
    principais_indicadores: List[str]
    recomendacoes: List[str]


class ModalityProjection(nn.Module):
    """Projeta embeddings de diferentes modalidades para espaço comum."""
    
    def __init__(
        self,
        video_dim: int = 768,
        audio_dim: int = 512,
        text_dim: int = 768,
        common_dim: int = 512
    ):
        """
        Inicializa projeções para espaço comum.
        
        Args:
            video_dim: Dimensão embeddings de vídeo
            audio_dim: Dimensão embeddings de áudio
            text_dim: Dimensão embeddings de texto
            common_dim: Dimensão do espaço comum
        """
        super().__init__()
        
        # Projeções lineares
        self.video_proj = nn.Sequential(
            nn.Linear(video_dim, common_dim),
            nn.LayerNorm(common_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        self.audio_proj = nn.Sequential(
            nn.Linear(audio_dim, common_dim),
            nn.LayerNorm(common_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        self.text_proj = nn.Sequential(
            nn.Linear(text_dim, common_dim),
            nn.LayerNorm(common_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
    
    def forward(
        self,
        video_emb: Optional[torch.Tensor] = None,
        audio_emb: Optional[torch.Tensor] = None,
        text_emb: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Projeta embeddings para espaço comum.
        
        Returns:
            Dict com embeddings projetados
        """
        projected = {}
        
        if video_emb is not None:
            projected['video'] = self.video_proj(video_emb)
        
        if audio_emb is not None:
            projected['audio'] = self.audio_proj(audio_emb)
        
        if text_emb is not None:
            projected['text'] = self.text_proj(text_emb)
        
        return projected


class CrossModalAttention(nn.Module):
    """Attention entre modalidades (cross-attention)."""
    
    def __init__(self, embed_dim: int = 512, num_heads: int = 8):
        """
        Inicializa cross-modal attention.
        
        Args:
            embed_dim: Dimensão dos embeddings
            num_heads: Número de attention heads
        """
        super().__init__()
        
        self.multihead_attn = nn.MultiheadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            dropout=0.1,
            batch_first=True
        )
        
        self.norm = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(0.1)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Cross-attention entre modalidades.
        
        Args:
            query: [batch, seq_len, dim]
            key: [batch, seq_len, dim]
            value: [batch, seq_len, dim]
        
        Returns:
            attended_output: [batch, seq_len, dim]
            attention_weights: [batch, num_heads, seq_len, seq_len]
        """
        # Multi-head attention
        attn_output, attn_weights = self.multihead_attn(
            query, key, value, need_weights=True, average_attn_weights=True
        )
        
        # Residual connection + normalization
        output = self.norm(query + self.dropout(attn_output))
        
        return output, attn_weights


class TransformerFusion(nn.Module):
    """Fusão baseada em Transformer com attention entre modalidades."""
    
    def __init__(
        self,
        embed_dim: int = 512,
        num_heads: int = 8,
        num_layers: int = 3,
        num_classes: int = 1  # Regressão: probabilidade de TEA
    ):
        """
        Inicializa Transformer para fusão multimodal.
        
        Args:
            embed_dim: Dimensão dos embeddings
            num_heads: Número de attention heads
            num_layers: Número de camadas Transformer
            num_classes: Número de classes de saída (1 para regressão)
        """
        super().__init__()
        
        self.embed_dim = embed_dim
        
        # Modality embeddings (como positional embeddings)
        self.modality_embeddings = nn.Embedding(3, embed_dim)  # 3 modalidades
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=0.1,
            activation='gelu',
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(embed_dim // 2, embed_dim // 4),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(embed_dim // 4, num_classes),
            nn.Sigmoid()  # Output: 0-1 (probabilidade)
        )
        
        # Attention pooling para extrair embedding final
        self.attention_pool = nn.MultiheadAttention(
            embed_dim=embed_dim,
            num_heads=1,
            batch_first=True
        )
        self.pool_query = nn.Parameter(torch.randn(1, 1, embed_dim))
    
    def forward(
        self,
        projected_embeddings: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Fusão multimodal via Transformer.
        
        Args:
            projected_embeddings: Dict com embeddings projetados
                {'video': [batch, dim], 'audio': [batch, dim], 'text': [batch, dim]}
        
        Returns:
            prediction: [batch, 1] - Probabilidade de TEA
            fused_embedding: [batch, dim] - Embedding fusionado
            attention_weights: [batch, num_modalities] - Importância de cada modalidade
        """
        batch_size = list(projected_embeddings.values())[0].shape[0]
        
        # Stack modalidades disponíveis
        modality_indices = []
        modality_tensors = []
        
        for idx, modality in enumerate(['video', 'audio', 'text']):
            if modality in projected_embeddings:
                modality_indices.append(idx)
                modality_tensors.append(projected_embeddings[modality])
        
        if not modality_tensors:
            raise ValueError("Nenhuma modalidade disponível")
        
        # [batch, num_modalities, dim]
        stacked = torch.stack(modality_tensors, dim=1)
        
        # Adicionar modality embeddings
        mod_emb = self.modality_embeddings(
            torch.tensor(modality_indices, device=stacked.device)
        )  # [num_modalities, dim]
        mod_emb = mod_emb.unsqueeze(0).expand(batch_size, -1, -1)  # [batch, num_mod, dim]
        
        stacked = stacked + mod_emb
        
        # Passar pelo Transformer
        transformer_output = self.transformer(stacked)  # [batch, num_mod, dim]
        
        # Attention pooling para obter embedding único
        pool_query_expanded = self.pool_query.expand(batch_size, -1, -1)
        fused_embedding, attn_weights = self.attention_pool(
            pool_query_expanded,
            transformer_output,
            transformer_output,
            need_weights=True,
            average_attn_weights=True
        )
        fused_embedding = fused_embedding.squeeze(1)  # [batch, dim]
        attn_weights = attn_weights.squeeze(1)  # [batch, num_mod]
        
        # Classificação
        prediction = self.classifier(fused_embedding)  # [batch, 1]
        
        return prediction, fused_embedding, attn_weights


class EarlyFusion(nn.Module):
    """Fusão precoce: concatenação de features."""
    
    def __init__(
        self,
        video_dim: int = 768,
        audio_dim: int = 512,
        text_dim: int = 768,
        hidden_dim: int = 512,
        num_classes: int = 1
    ):
        """
        Inicializa early fusion.
        
        Args:
            video_dim, audio_dim, text_dim: Dimensões dos embeddings
            hidden_dim: Dimensão da camada oculta
            num_classes: Número de classes (1 para regressão)
        """
        super().__init__()
        
        # Total dim quando todas modalidades presentes
        total_dim = video_dim + audio_dim + text_dim
        
        self.fusion_network = nn.Sequential(
            nn.Linear(total_dim, hidden_dim * 2),
            nn.BatchNorm1d(hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, num_classes),
            nn.Sigmoid()
        )
    
    def forward(
        self,
        video_emb: Optional[torch.Tensor] = None,
        audio_emb: Optional[torch.Tensor] = None,
        text_emb: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Concatena e classifica.
        
        Returns:
            prediction: [batch, 1]
        """
        # Concatenar modalidades disponíveis
        embeddings = []
        
        if video_emb is not None:
            embeddings.append(video_emb)
        if audio_emb is not None:
            embeddings.append(audio_emb)
        if text_emb is not None:
            embeddings.append(text_emb)
        
        if not embeddings:
            raise ValueError("Nenhuma modalidade disponível")
        
        concatenated = torch.cat(embeddings, dim=-1)  # [batch, total_dim]
        
        prediction = self.fusion_network(concatenated)
        
        return prediction


class LateFusion:
    """Fusão tardia: ensemble de predições individuais."""
    
    def __init__(self):
        """Inicializa late fusion (weighted voting)."""
        pass
    
    def fuse(
        self,
        predictions: Dict[str, float],
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Combina predições com pesos.
        
        Args:
            predictions: {'video': 0.7, 'audio': 0.5, 'text': 0.6}
            weights: Pesos opcionais por modalidade
        
        Returns:
            final_prediction: Média ponderada
        """
        if not predictions:
            return 0.5  # Neutro
        
        if weights is None:
            # Pesos uniformes
            weights = {mod: 1.0 / len(predictions) for mod in predictions}
        
        # Normalizar pesos
        total_weight = sum(weights.get(mod, 0) for mod in predictions)
        if total_weight == 0:
            total_weight = 1.0
        
        # Média ponderada
        final = sum(
            pred * weights.get(mod, 0) / total_weight
            for mod, pred in predictions.items()
        )
        
        return final


class MultimodalFusionPipeline:
    """Pipeline completo de fusão multimodal."""
    
    def __init__(
        self,
        fusion_method: str = 'transformer',  # 'transformer', 'early', 'late'
        device: str = 'cpu'
    ):
        """
        Inicializa pipeline de fusão.
        
        Args:
            fusion_method: Método de fusão ('transformer', 'early', 'late')
            device: 'cpu' ou 'cuda'
        """
        self.fusion_method = fusion_method
        self.device = torch.device(device)
        
        # Componentes
        self.projection = ModalityProjection()
        
        if fusion_method == 'transformer':
            self.fusion_model = TransformerFusion()
        elif fusion_method == 'early':
            self.fusion_model = EarlyFusion()
        elif fusion_method == 'late':
            self.fusion_model = LateFusion()
        else:
            raise ValueError(f"Método inválido: {fusion_method}")
        
        # Mover para device
        if fusion_method != 'late':
            self.projection.to(self.device)
            self.fusion_model.to(self.device)
            self.projection.eval()
            self.fusion_model.eval()
    
    def fuse(
        self,
        features: MultimodalFeatures,
        return_embeddings: bool = True
    ) -> FusionResult:
        """
        Fusão multimodal completa.
        
        Args:
            features: MultimodalFeatures com embeddings e scores
            return_embeddings: Se deve retornar embeddings fusionados
        
        Returns:
            FusionResult com classificação final
        """
        # 1. Preparar tensors
        tensors = self._prepare_tensors(features)
        
        # 2. Aplicar fusão
        if self.fusion_method == 'late':
            score_final, attention_weights, fused_emb = self._late_fusion(features, tensors)
        elif self.fusion_method == 'early':
            score_final, attention_weights, fused_emb = self._early_fusion(tensors)
        else:  # transformer
            score_final, attention_weights, fused_emb = self._transformer_fusion(tensors)
        
        # 3. Calcular confiança
        confianca = self._calculate_confidence(
            score_final,
            attention_weights,
            features.available_modalities
        )
        
        # 4. Classificar nível de risco
        nivel_risco = self._classify_risk(score_final)
        
        # 5. Extrair scores por modalidade
        scores_modalidades = {
            'video': features.video_score,
            'audio': features.audio_score,
            'text': features.text_score
        }
        scores_modalidades = {k: v for k, v in scores_modalidades.items() if v is not None}
        
        # 6. Gerar explicações
        principais_indicadores = self._extract_indicators(
            features, attention_weights, score_final
        )
        recomendacoes = self._generate_recommendations(nivel_risco, principais_indicadores)
        
        return FusionResult(
            score_final=score_final,
            nivel_risco=nivel_risco,
            confianca=confianca,
            scores_modalidades=scores_modalidades,
            attention_weights=attention_weights,
            fused_embeddings=fused_emb if return_embeddings else np.array([]),
            principais_indicadores=principais_indicadores,
            recomendacoes=recomendacoes
        )
    
    def _prepare_tensors(self, features: MultimodalFeatures) -> Dict[str, torch.Tensor]:
        """Converte numpy arrays para tensors PyTorch."""
        tensors = {}
        
        if features.video_embeddings is not None:
            tensors['video'] = torch.from_numpy(features.video_embeddings).float().unsqueeze(0).to(self.device)
        
        if features.audio_embeddings is not None:
            tensors['audio'] = torch.from_numpy(features.audio_embeddings).float().unsqueeze(0).to(self.device)
        
        if features.text_embeddings is not None:
            tensors['text'] = torch.from_numpy(features.text_embeddings).float().unsqueeze(0).to(self.device)
        
        return tensors
    
    def _transformer_fusion(
        self, 
        tensors: Dict[str, torch.Tensor]
    ) -> Tuple[float, Dict[str, float], np.ndarray]:
        """Fusão via Transformer."""
        with torch.no_grad():
            # Projetar para espaço comum
            projected = self.projection(**tensors)
            
            # Fusão Transformer
            prediction, fused_emb, attn_weights = self.fusion_model(projected)
            
            score = float(prediction.squeeze().cpu().numpy())
            fused_emb_np = fused_emb.squeeze().cpu().numpy()
            
            # Converter attention weights para dict
            attn_dict = {}
            for idx, modality in enumerate(['video', 'audio', 'text']):
                if modality in projected:
                    attn_dict[modality] = float(attn_weights[0, idx].cpu().numpy())
        
        return score, attn_dict, fused_emb_np
    
    def _early_fusion(
        self, 
        tensors: Dict[str, torch.Tensor]
    ) -> Tuple[float, Dict[str, float], np.ndarray]:
        """Fusão precoce (concatenação)."""
        with torch.no_grad():
            prediction = self.fusion_model(**tensors)
            score = float(prediction.squeeze().cpu().numpy())
            
            # Concatenar embeddings originais como "fused"
            embeddings = [t.squeeze().cpu().numpy() for t in tensors.values()]
            fused_emb = np.concatenate(embeddings)
            
            # Attention weights uniformes
            num_modalities = len(tensors)
            attn_dict = {mod: 1.0 / num_modalities for mod in tensors.keys()}
        
        return score, attn_dict, fused_emb
    
    def _late_fusion(
        self,
        features: MultimodalFeatures,
        tensors: Dict[str, torch.Tensor]
    ) -> Tuple[float, Dict[str, float], np.ndarray]:
        """Fusão tardia (ensemble de scores)."""
        # Coletar scores individuais
        predictions = {}
        if features.video_score is not None:
            predictions['video'] = 1.0 - features.video_score  # Inverter: score alto = baixo risco
        if features.audio_score is not None:
            predictions['audio'] = 1.0 - features.audio_score
        if features.text_score is not None:
            predictions['text'] = 1.0 - features.text_score
        
        # Pesos baseados em confiabilidade (fixos ou aprendidos)
        weights = {'video': 0.4, 'audio': 0.3, 'text': 0.3}
        
        # Ensemble
        score = self.fusion_model.fuse(predictions, weights)
        
        # Concatenar embeddings
        embeddings = [t.squeeze().cpu().numpy() for t in tensors.values()]
        fused_emb = np.concatenate(embeddings) if embeddings else np.array([])
        
        # Attention = pesos normalizados
        attn_dict = {mod: weights.get(mod, 0) for mod in predictions}
        
        return score, attn_dict, fused_emb
    
    def _calculate_confidence(
        self,
        score: float,
        attention_weights: Dict[str, float],
        available_modalities: List[str]
    ) -> float:
        """Calcula confiança da predição."""
        # Confiança baseada em:
        # 1. Número de modalidades (mais modalidades = mais confiança)
        # 2. Distribuição de attention weights (uniforme = menos confiança)
        # 3. Extremidade do score (0.1 ou 0.9 = alta confiança, 0.5 = baixa)
        
        num_modalities = len(available_modalities)
        max_modalities = 3
        modality_factor = num_modalities / max_modalities
        
        # Entropia de attention weights (baixa entropia = alta confiança)
        if attention_weights:
            weights = list(attention_weights.values())
            entropy = -sum(w * np.log(w + 1e-8) for w in weights)
            max_entropy = np.log(len(weights))
            attention_factor = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 0.5
        else:
            attention_factor = 0.5
        
        # Distância do score em relação a 0.5 (decisão boundary)
        score_certainty = abs(score - 0.5) * 2  # 0-1
        
        # Combinar fatores
        confidence = (modality_factor * 0.3 + attention_factor * 0.3 + score_certainty * 0.4)
        
        return confidence
    
    def _classify_risk(self, score: float) -> str:
        """Classifica nível de risco baseado no score."""
        if score < 0.3:
            return 'baixo'
        elif score < 0.6:
            return 'medio'
        else:
            return 'alto'
    
    def _extract_indicators(
        self,
        features: MultimodalFeatures,
        attention_weights: Dict[str, float],
        score: float
    ) -> List[str]:
        """Extrai principais indicadores baseados em attention."""
        indicators = []
        
        # Ordenar modalidades por attention weight
        sorted_modalities = sorted(
            attention_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for modality, weight in sorted_modalities:
            if weight > 0.2:  # Contribuição significativa
                if modality == 'video':
                    indicators.append(f"Padrões visuais atípicos (peso: {weight:.2f})")
                elif modality == 'audio':
                    indicators.append(f"Padrões prosódicos atípicos (peso: {weight:.2f})")
                elif modality == 'text':
                    indicators.append(f"Padrões linguísticos de preocupação (peso: {weight:.2f})")
        
        if score > 0.6:
            indicators.append("Score de risco elevado detectado")
        
        return indicators
    
    def _generate_recommendations(
        self,
        nivel_risco: str,
        indicadores: List[str]
    ) -> List[str]:
        """Gera recomendações baseadas no nível de risco."""
        recommendations = []
        
        if nivel_risco == 'alto':
            recommendations.append("⚠️ Recomenda-se avaliação diagnóstica completa com equipe multidisciplinar")
            recommendations.append("Agendar consulta com neuropediatra e psicólogo especializado em TEA")
            recommendations.append("Iniciar intervenção precoce mesmo antes do diagnóstico formal")
        
        elif nivel_risco == 'medio':
            recommendations.append("⚠️ Monitoramento contínuo recomendado")
            recommendations.append("Considerar avaliação com pediatra especializado em desenvolvimento")
            recommendations.append("Reavaliar em 3-6 meses")
        
        else:  # baixo
            recommendations.append("✓ Resultados dentro dos padrões esperados")
            recommendations.append("Manter acompanhamento pediátrico de rotina")
            recommendations.append("Reavaliar caso surjam novas preocupações")
        
        return recommendations


# Exemplo de uso
if __name__ == "__main__":
    # Criar features multimodais de exemplo
    features = MultimodalFeatures(
        video_embeddings=np.random.randn(768),
        video_score=0.7,
        audio_embeddings=np.random.randn(512),
        audio_score=0.6,
        text_embeddings=np.random.randn(768),
        text_score=0.8,
        available_modalities=['video', 'audio', 'text']
    )
    
    # Testar diferentes métodos de fusão
    for method in ['transformer', 'early', 'late']:
        print(f"\n{'='*60}")
        print(f"Método de Fusão: {method.upper()}")
        print(f"{'='*60}")
        
        pipeline = MultimodalFusionPipeline(fusion_method=method)
        result = pipeline.fuse(features)
        
        print(f"Score Final: {result.score_final:.3f}")
        print(f"Nível de Risco: {result.nivel_risco.upper()}")
        print(f"Confiança: {result.confianca:.3f}")
        print(f"\nAttention Weights:")
        for mod, weight in result.attention_weights.items():
            print(f"  {mod}: {weight:.3f}")
        print(f"\nIndicadores:")
        for ind in result.principais_indicadores:
            print(f"  • {ind}")
        print(f"\nRecomendações:")
        for rec in result.recomendacoes:
            print(f"  {rec}")
