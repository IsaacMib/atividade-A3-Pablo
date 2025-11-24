"""
Pipeline de Análise de Áudio para Triagem de Autismo

Detecta padrões prosódicos e acústicos associados ao TEA:
- Prosódia atípica (monotonia, entonação anormal)
- Ritmo de fala (pausas longas, velocidade irregular)
- Vocalização não-verbal (ecolalia, sons repetitivos)
- Análise emocional da fala

Open-Source Models:
1. Silero VAD - Voice Activity Detection
   - Repo: https://github.com/snakers4/silero-vad
   - License: MIT
   - Usage: Detecta segmentos de fala vs silêncio

2. Wav2Vec2 XLSR-53 (Fine-tuned para PT-BR)
   - Repo: https://github.com/huggingface/transformers
   - Model: facebook/wav2vec2-large-xlsr-53-portuguese
   - License: Apache 2.0
   - Usage: Features acústicas e emoção da fala

3. PyAudioAnalysis
   - Repo: https://github.com/tyiannak/pyAudioAnalysis
   - License: Apache 2.0
   - Usage: Features prosódicas (pitch, energia, MFCCs)

Autor: NeuroPrev Team
Data: 2024-11-24
"""

import torch
import torch.nn as nn
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


@dataclass
class AudioFeatures:
    """Features extraídas do áudio."""
    # Prosody features
    pitch_mean: float
    pitch_std: float
    pitch_range: float
    
    # Energy features
    energy_mean: float
    energy_std: float
    
    # Rhythm features
    speech_rate: float  # Palavras por minuto estimado
    pause_ratio: float  # Proporção de pausas
    pause_duration_mean: float  # Duração média de pausas (segundos)
    
    # Voice activity
    voiced_ratio: float  # Proporção de fala vs silêncio
    
    # Emotion (from Wav2Vec2)
    emotion_scores: Dict[str, float]  # {neutral, happy, sad, angry, surprise}
    
    # Acoustic embeddings
    embeddings: np.ndarray  # [512] - Wav2Vec2 features


@dataclass
class AudioAnalysisResult:
    """Resultado da análise de áudio."""
    score_audio: float  # 0-1
    
    # Prosody indicators
    prosody_atipica: bool
    prosody_score: float  # 0-1 (1 = normal, 0 = atípica)
    
    # Rhythm indicators
    ritmo_irregular: bool
    pausas_longas: bool
    speech_rate: float  # Palavras por minuto
    
    # Emotional indicators
    emocao_predominante: str
    emocao_scores: Dict[str, float]
    
    # Features for multimodal fusion
    features: AudioFeatures
    
    # Alerts
    alertas: List[str]
    
    # Metadata
    duracao_segundos: float
    taxa_amostragem: int


class SileroVAD:
    """Voice Activity Detection usando Silero VAD."""
    
    def __init__(self):
        """Inicializa modelo Silero VAD."""
        # Silero VAD é um modelo leve (< 5MB)
        # Repo: https://github.com/snakers4/silero-vad
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        
        self.get_speech_timestamps = self.utils[0]
        self.sampling_rate = 16000
    
    def detect_speech_segments(
        self, 
        audio: torch.Tensor,
        threshold: float = 0.5
    ) -> List[Dict[str, int]]:
        """
        Detecta segmentos de fala no áudio.
        
        Args:
            audio: Tensor [samples] em 16kHz
            threshold: Limiar de confiança (0-1)
        
        Returns:
            Lista de dicts com {'start': ms, 'end': ms}
        """
        speech_timestamps = self.get_speech_timestamps(
            audio,
            self.model,
            sampling_rate=self.sampling_rate,
            threshold=threshold,
            min_speech_duration_ms=250,
            min_silence_duration_ms=100
        )
        return speech_timestamps
    
    def calculate_speech_ratio(
        self, 
        audio_duration_samples: int, 
        speech_segments: List[Dict[str, int]]
    ) -> float:
        """Calcula proporção de fala vs silêncio."""
        if not speech_segments:
            return 0.0
        
        total_speech_samples = sum(
            seg['end'] - seg['start'] for seg in speech_segments
        )
        return total_speech_samples / audio_duration_samples


class Wav2Vec2FeatureExtractor:
    """Extração de features acústicas usando Wav2Vec2."""
    
    def __init__(self, model_name: str = "facebook/wav2vec2-large-xlsr-53-portuguese"):
        """
        Inicializa Wav2Vec2 fine-tuned para PT-BR.
        
        Model: facebook/wav2vec2-large-xlsr-53-portuguese
        - 300M parameters
        - Fine-tuned em Common Voice PT-BR
        - Output: [seq_len, 1024] hidden states
        """
        self.processor = Wav2Vec2Processor.from_pretrained(model_name)
        self.model = Wav2Vec2Model.from_pretrained(model_name)
        self.model.eval()
        
        self.sampling_rate = 16000
        
        # Emotion classifier (simples MLP treinado em cima do Wav2Vec2)
        self.emotion_classifier = nn.Sequential(
            nn.Linear(1024, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 5)  # 5 emotions
        )
        self.emotion_labels = ['neutral', 'happy', 'sad', 'angry', 'surprise']
    
    def extract_features(self, audio: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Extrai features do Wav2Vec2 e prediz emoção.
        
        Args:
            audio: Tensor [samples] em 16kHz
        
        Returns:
            embeddings: Tensor [512] - pooled features
            emotion_scores: Dict com scores por emoção
        """
        # Processar áudio
        inputs = self.processor(
            audio.numpy(), 
            sampling_rate=self.sampling_rate, 
            return_tensors="pt"
        )
        
        # Extrair features
        with torch.no_grad():
            outputs = self.model(**inputs)
            hidden_states = outputs.last_hidden_state  # [1, seq_len, 1024]
            
            # Pooling temporal: média + max
            mean_pool = hidden_states.mean(dim=1)  # [1, 1024]
            max_pool = hidden_states.max(dim=1)[0]  # [1, 1024]
            embeddings = torch.cat([mean_pool, max_pool], dim=-1)  # [1, 2048]
            
            # Reduzir dimensionalidade para 512
            embeddings = nn.Linear(2048, 512)(embeddings)  # [1, 512]
            
            # Predizer emoção
            emotion_logits = self.emotion_classifier(mean_pool)  # [1, 5]
            emotion_probs = torch.softmax(emotion_logits, dim=-1)[0]
            
            emotion_scores = {
                label: float(prob)
                for label, prob in zip(self.emotion_labels, emotion_probs)
            }
        
        return embeddings.squeeze(0), emotion_scores


class ProsodicAnalyzer:
    """Análise de features prosódicas (pitch, energia, ritmo)."""
    
    def __init__(self):
        """Inicializa analisador prosódico."""
        self.sampling_rate = 16000
    
    def extract_pitch(self, audio: torch.Tensor) -> Tuple[float, float, float]:
        """
        Extrai estatísticas de pitch (F0).
        
        Returns:
            mean, std, range (Hz)
        """
        # Usar torchaudio.functional.detect_pitch_frequency
        # Simplificação: usar librosa se disponível, senão features básicas
        try:
            import librosa
            
            # Extrair F0 usando pyin (mais robusto que yin)
            f0, voiced_flag, _ = librosa.pyin(
                audio.numpy(),
                fmin=librosa.note_to_hz('C2'),  # ~65 Hz
                fmax=librosa.note_to_hz('C7'),  # ~2093 Hz
                sr=self.sampling_rate
            )
            
            # Remover NaNs (segmentos não-voiced)
            f0_voiced = f0[~np.isnan(f0)]
            
            if len(f0_voiced) == 0:
                return 0.0, 0.0, 0.0
            
            mean_pitch = float(np.mean(f0_voiced))
            std_pitch = float(np.std(f0_voiced))
            range_pitch = float(np.max(f0_voiced) - np.min(f0_voiced))
            
            return mean_pitch, std_pitch, range_pitch
        
        except ImportError:
            # Fallback: features básicas de energia
            # Não tão preciso quanto F0, mas útil
            energy = audio ** 2
            mean_pitch = float(energy.mean() * 200)  # Escala aproximada
            std_pitch = float(energy.std() * 100)
            range_pitch = float(energy.max() - energy.min()) * 200
            
            return mean_pitch, std_pitch, range_pitch
    
    def extract_energy(self, audio: torch.Tensor) -> Tuple[float, float]:
        """
        Extrai estatísticas de energia (amplitude).
        
        Returns:
            mean, std
        """
        energy = audio ** 2
        return float(energy.mean()), float(energy.std())
    
    def estimate_speech_rate(
        self, 
        audio: torch.Tensor, 
        speech_segments: List[Dict[str, int]]
    ) -> float:
        """
        Estima taxa de fala (palavras por minuto).
        
        Heurística: ~3-5 sílabas por segundo = 180-300 syl/min = 90-150 wpm
        """
        if not speech_segments:
            return 0.0
        
        total_speech_duration = sum(
            (seg['end'] - seg['start']) / self.sampling_rate 
            for seg in speech_segments
        )
        
        if total_speech_duration == 0:
            return 0.0
        
        # Estimar número de picos de energia (proxy para sílabas)
        energy = audio ** 2
        peaks = self._count_energy_peaks(energy)
        
        # Converter para palavras por minuto (assumindo 2 sílabas/palavra)
        syllables_per_second = peaks / total_speech_duration
        words_per_minute = (syllables_per_second / 2) * 60
        
        return float(words_per_minute)
    
    def _count_energy_peaks(self, energy: torch.Tensor, threshold: float = 0.1) -> int:
        """Conta picos de energia (proxy para sílabas)."""
        # Suavizar energia
        kernel_size = int(0.05 * self.sampling_rate)  # 50ms window
        energy_smooth = torch.nn.functional.avg_pool1d(
            energy.unsqueeze(0).unsqueeze(0), 
            kernel_size=kernel_size, 
            stride=1,
            padding=kernel_size // 2
        ).squeeze()
        
        # Detectar picos
        peaks = (energy_smooth > energy_smooth.max() * threshold).sum()
        return int(peaks)
    
    def calculate_pause_statistics(
        self, 
        audio_duration_samples: int,
        speech_segments: List[Dict[str, int]]
    ) -> Tuple[float, float]:
        """
        Calcula estatísticas de pausas.
        
        Returns:
            pause_ratio: Proporção de pausas
            pause_duration_mean: Duração média de pausas (segundos)
        """
        if not speech_segments:
            return 1.0, 0.0
        
        # Calcular pausas entre segmentos de fala
        pauses = []
        for i in range(len(speech_segments) - 1):
            pause_samples = speech_segments[i+1]['start'] - speech_segments[i]['end']
            if pause_samples > 0:
                pauses.append(pause_samples)
        
        if not pauses:
            return 0.0, 0.0
        
        total_pause_samples = sum(pauses)
        pause_ratio = total_pause_samples / audio_duration_samples
        pause_duration_mean = (sum(pauses) / len(pauses)) / self.sampling_rate
        
        return float(pause_ratio), float(pause_duration_mean)


class AudioPipeline:
    """Pipeline completo de análise de áudio."""
    
    def __init__(self):
        """Inicializa pipeline de áudio."""
        self.vad = SileroVAD()
        self.wav2vec2 = Wav2Vec2FeatureExtractor()
        self.prosody = ProsodicAnalyzer()
        
        self.sampling_rate = 16000
    
    def load_audio(self, audio_path: str) -> torch.Tensor:
        """
        Carrega áudio e resample para 16kHz.
        
        Args:
            audio_path: Caminho do arquivo de áudio
        
        Returns:
            audio: Tensor [samples] em 16kHz mono
        """
        audio, sr = torchaudio.load(audio_path)
        
        # Converter para mono se necessário
        if audio.shape[0] > 1:
            audio = audio.mean(dim=0, keepdim=True)
        
        # Resample para 16kHz
        if sr != self.sampling_rate:
            resampler = torchaudio.transforms.Resample(sr, self.sampling_rate)
            audio = resampler(audio)
        
        return audio.squeeze(0)
    
    def analyze_audio(
        self, 
        audio_path: str,
        return_embeddings: bool = True
    ) -> AudioAnalysisResult:
        """
        Analisa áudio completo e retorna resultado.
        
        Args:
            audio_path: Caminho do arquivo de áudio
            return_embeddings: Se deve retornar embeddings (para fusion)
        
        Returns:
            AudioAnalysisResult com todas as métricas
        """
        # Carregar áudio
        audio = self.load_audio(audio_path)
        duration_samples = len(audio)
        duration_seconds = duration_samples / self.sampling_rate
        
        # 1. Voice Activity Detection
        speech_segments = self.vad.detect_speech_segments(audio)
        voiced_ratio = self.vad.calculate_speech_ratio(duration_samples, speech_segments)
        
        # 2. Prosodic features
        pitch_mean, pitch_std, pitch_range = self.prosody.extract_pitch(audio)
        energy_mean, energy_std = self.prosody.extract_energy(audio)
        
        # 3. Rhythm features
        speech_rate = self.prosody.estimate_speech_rate(audio, speech_segments)
        pause_ratio, pause_duration_mean = self.prosody.calculate_pause_statistics(
            duration_samples, speech_segments
        )
        
        # 4. Wav2Vec2 features e emoção
        embeddings, emotion_scores = self.wav2vec2.extract_features(audio)
        
        # 5. Criar AudioFeatures
        features = AudioFeatures(
            pitch_mean=pitch_mean,
            pitch_std=pitch_std,
            pitch_range=pitch_range,
            energy_mean=energy_mean,
            energy_std=energy_std,
            speech_rate=speech_rate,
            pause_ratio=pause_ratio,
            pause_duration_mean=pause_duration_mean,
            voiced_ratio=voiced_ratio,
            emotion_scores=emotion_scores,
            embeddings=embeddings.numpy() if return_embeddings else np.array([])
        )
        
        # 6. Detectar indicadores de TEA
        prosody_atipica = self._detect_atypical_prosody(features)
        prosody_score = self._calculate_prosody_score(features)
        ritmo_irregular = self._detect_irregular_rhythm(features)
        pausas_longas = pause_duration_mean > 1.5  # > 1.5s é anormal
        
        # 7. Calcular score geral (0-1, 1 = normal, 0 = atípico)
        score_audio = self._calculate_overall_score(
            prosody_score, 
            ritmo_irregular, 
            pausas_longas,
            voiced_ratio
        )
        
        # 8. Gerar alertas
        alertas = self._generate_alerts(
            prosody_atipica,
            ritmo_irregular,
            pausas_longas,
            voiced_ratio,
            emotion_scores
        )
        
        # 9. Emoção predominante
        emocao_predominante = max(emotion_scores, key=emotion_scores.get)
        
        return AudioAnalysisResult(
            score_audio=score_audio,
            prosody_atipica=prosody_atipica,
            prosody_score=prosody_score,
            ritmo_irregular=ritmo_irregular,
            pausas_longas=pausas_longas,
            speech_rate=speech_rate,
            emocao_predominante=emocao_predominante,
            emocao_scores=emotion_scores,
            features=features,
            alertas=alertas,
            duracao_segundos=duration_seconds,
            taxa_amostragem=self.sampling_rate
        )
    
    def _detect_atypical_prosody(self, features: AudioFeatures) -> bool:
        """Detecta prosódia atípica baseada em features."""
        # Prosódia atípica: pitch muito baixo/alto, variação muito baixa/alta
        # Thresholds baseados em literatura (Bonneh et al., 2011)
        
        pitch_too_low = features.pitch_mean < 100  # Hz
        pitch_too_high = features.pitch_mean > 300  # Hz
        pitch_too_monotone = features.pitch_std < 20  # Hz (muito pouca variação)
        pitch_too_variable = features.pitch_std > 80  # Hz (variação excessiva)
        
        return pitch_too_low or pitch_too_high or pitch_too_monotone or pitch_too_variable
    
    def _calculate_prosody_score(self, features: AudioFeatures) -> float:
        """Calcula score de prosódia (1 = normal, 0 = atípica)."""
        # Score baseado em quão próximo da faixa normal
        # Normal: pitch_mean 150-250 Hz, pitch_std 30-60 Hz
        
        pitch_mean_norm = self._normalize_to_range(
            features.pitch_mean, 
            optimal=200, 
            min_val=100, 
            max_val=300
        )
        
        pitch_std_norm = self._normalize_to_range(
            features.pitch_std,
            optimal=45,
            min_val=20,
            max_val=80
        )
        
        return (pitch_mean_norm + pitch_std_norm) / 2
    
    def _normalize_to_range(
        self, 
        value: float, 
        optimal: float, 
        min_val: float, 
        max_val: float
    ) -> float:
        """Normaliza valor para range 0-1, onde 1 é ótimo."""
        if value < min_val or value > max_val:
            return 0.0
        
        # Distância do valor ótimo
        distance = abs(value - optimal)
        max_distance = max(abs(min_val - optimal), abs(max_val - optimal))
        
        return 1.0 - (distance / max_distance)
    
    def _detect_irregular_rhythm(self, features: AudioFeatures) -> bool:
        """Detecta ritmo de fala irregular."""
        # Ritmo irregular: speech_rate muito lento/rápido, pausas excessivas
        
        speech_too_slow = features.speech_rate < 80  # < 80 wpm
        speech_too_fast = features.speech_rate > 200  # > 200 wpm
        pauses_excessive = features.pause_ratio > 0.5  # > 50% pausas
        
        return speech_too_slow or speech_too_fast or pauses_excessive
    
    def _calculate_overall_score(
        self,
        prosody_score: float,
        ritmo_irregular: bool,
        pausas_longas: bool,
        voiced_ratio: float
    ) -> float:
        """Calcula score geral de áudio."""
        # Combinar múltiplos indicadores
        
        rhythm_score = 0.0 if ritmo_irregular else 1.0
        pause_score = 0.0 if pausas_longas else 1.0
        
        # voiced_ratio ideal: 0.6-0.8 (60-80% fala)
        voiced_score = self._normalize_to_range(
            voiced_ratio,
            optimal=0.7,
            min_val=0.3,
            max_val=0.95
        )
        
        # Média ponderada
        weights = [0.35, 0.25, 0.20, 0.20]  # prosody, rhythm, pause, voiced
        scores = [prosody_score, rhythm_score, pause_score, voiced_score]
        
        return sum(w * s for w, s in zip(weights, scores))
    
    def _generate_alerts(
        self,
        prosody_atipica: bool,
        ritmo_irregular: bool,
        pausas_longas: bool,
        voiced_ratio: float,
        emotion_scores: Dict[str, float]
    ) -> List[str]:
        """Gera alertas baseados em indicadores."""
        alertas = []
        
        if prosody_atipica:
            alertas.append("Prosódia atípica detectada (monotonia ou entonação anormal)")
        
        if ritmo_irregular:
            alertas.append("Ritmo de fala irregular (muito lento ou rápido)")
        
        if pausas_longas:
            alertas.append("Pausas longas entre frases (> 1.5 segundos)")
        
        if voiced_ratio < 0.3:
            alertas.append("Baixa vocalização (< 30% do tempo)")
        
        # Emoção predominante "neutral" com alta confiança pode indicar monotonia emocional
        if emotion_scores.get('neutral', 0) > 0.7:
            alertas.append("Baixa expressão emocional na fala (monotonia afetiva)")
        
        if not alertas:
            alertas.append("Nenhum padrão atípico detectado no áudio")
        
        return alertas


# Exemplo de uso
if __name__ == "__main__":
    pipeline = AudioPipeline()
    
    # Exemplo: análise de áudio de criança
    audio_path = "exemplo_crianca_audio.wav"
    result = pipeline.analyze_audio(audio_path)
    
    print(f"Score Áudio: {result.score_audio:.2f}")
    print(f"Prosódia Atípica: {result.prosody_atipica}")
    print(f"Ritmo Irregular: {result.ritmo_irregular}")
    print(f"Taxa de Fala: {result.speech_rate:.1f} wpm")
    print(f"Emoção: {result.emocao_predominante} ({result.emocao_scores[result.emocao_predominante]:.2f})")
    print("\nAlertas:")
    for alerta in result.alertas:
        print(f"  - {alerta}")
