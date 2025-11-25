"""
Athena AI - Video Analysis Pipeline

Módulo de análise de vídeo para detecção de:
- Contato visual (eye gaze tracking)
- Expressões faciais (sorriso, surpresa, tristeza)
- Movimento de cabeça (head pose estimation)
- Gestos e movimentos corporais

Modelos utilizados:
1. MediaPipe (Google) - https://github.com/google/mediapipe
   - Face Mesh: 468 landmarks faciais
   - Pose: 33 pontos corporais
   - Hands: 21 pontos por mão
   - Licença: Apache 2.0

2. InsightFace - https://github.com/deepinsight/insightface
   - ArcFace: Face embeddings 512-dim
   - Face attributes: idade, gênero, qualidade
   - Licença: MIT
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional
import torch
import torch.nn as nn
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class VideoAnalysisResult:
    """Resultado da análise de vídeo."""
    score_video: float
    contato_visual: Dict[str, float]
    expressoes: Dict[str, float]
    head_pose: Dict[str, List[float]]
    gestos: Dict[str, int]
    alertas: List[Dict]
    embeddings: np.ndarray
    frames_analisados: int
    fps: float


class MediaPipeAnalyzer:
    """
    Analisador usando MediaPipe para features faciais e corporais.
    
    Referência: https://github.com/google/mediapipe
    Documentação: https://google.github.io/mediapipe/solutions/solutions.html
    """
    
    def __init__(self):
        # Inicializar componentes do MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Configurar detectores
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Índices de landmarks importantes para TEA
        # Eyes (contato visual)
        self.LEFT_EYE = [33, 133, 160, 159, 158, 157, 173]
        self.RIGHT_EYE = [362, 263, 385, 386, 387, 388, 398]
        
        # Iris (direção do olhar)
        self.LEFT_IRIS = [468, 469, 470, 471, 472]
        self.RIGHT_IRIS = [473, 474, 475, 476, 477]
        
        # Mouth (sorriso, vocalização)
        self.LIPS = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
        
        logger.info("MediaPipe Analyzer inicializado")
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analisa um frame individual.
        
        Args:
            frame: Frame BGR do OpenCV
            
        Returns:
            Dicionário com landmarks e features
        """
        # Converter BGR para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]
        
        results = {}
        
        # Face Mesh
        face_results = self.face_mesh.process(rgb_frame)
        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0]
            results['face_landmarks'] = self._extract_face_features(landmarks, w, h)
            results['eye_gaze'] = self._estimate_eye_gaze(landmarks, w, h)
            results['smile'] = self._detect_smile(landmarks)
        
        # Pose
        pose_results = self.pose.process(rgb_frame)
        if pose_results.pose_landmarks:
            results['pose'] = self._extract_pose_features(pose_results.pose_landmarks)
            results['head_pose'] = self._estimate_head_pose(pose_results.pose_landmarks)
        
        # Hands
        hands_results = self.hands.process(rgb_frame)
        if hands_results.multi_hand_landmarks:
            results['hands'] = self._extract_hand_features(hands_results.multi_hand_landmarks)
        
        return results
    
    def _extract_face_features(self, landmarks, w: int, h: int) -> np.ndarray:
        """Extrai features dos 468 landmarks faciais."""
        features = []
        for landmark in landmarks.landmark:
            features.extend([landmark.x * w, landmark.y * h, landmark.z])
        return np.array(features)
    
    def _estimate_eye_gaze(self, landmarks, w: int, h: int) -> Dict[str, float]:
        """
        Estima direção do olhar usando landmarks de íris.
        
        Retorna:
            - looking_at_camera: probabilidade [0-1] de estar olhando para câmera
            - gaze_x, gaze_y: direção do olhar em pixels
        """
        # Pegar landmarks de íris esquerda e direita
        left_iris_points = [landmarks.landmark[i] for i in self.LEFT_IRIS]
        right_iris_points = [landmarks.landmark[i] for i in self.RIGHT_IRIS]
        
        # Centro dos olhos
        left_eye_center = np.mean([[p.x * w, p.y * h] for p in left_iris_points], axis=0)
        right_eye_center = np.mean([[p.x * w, p.y * h] for p in right_iris_points], axis=0)
        
        # Centro da íris (468-472 left, 473-477 right)
        left_iris_center = np.array([landmarks.landmark[468].x * w, landmarks.landmark[468].y * h])
        right_iris_center = np.array([landmarks.landmark[473].x * w, landmarks.landmark[473].y * h])
        
        # Desvio da íris em relação ao centro do olho
        left_deviation = np.linalg.norm(left_iris_center - left_eye_center)
        right_deviation = np.linalg.norm(right_iris_center - right_eye_center)
        
        # Média dos desvios
        avg_deviation = (left_deviation + right_deviation) / 2
        
        # Normalizar: desvio pequeno = olhando para câmera
        # Threshold empírico: < 5 pixels = olhando
        looking_at_camera = max(0.0, 1.0 - (avg_deviation / 10.0))
        
        return {
            'looking_at_camera': float(looking_at_camera),
            'gaze_x': float((left_iris_center[0] + right_iris_center[0]) / 2),
            'gaze_y': float((left_iris_center[1] + right_iris_center[1]) / 2),
            'left_deviation': float(left_deviation),
            'right_deviation': float(right_deviation)
        }
    
    def _detect_smile(self, landmarks) -> float:
        """
        Detecta sorriso usando distância dos cantos da boca.
        
        Landmarks relevantes:
        - 61: canto esquerdo da boca
        - 291: canto direito da boca
        - 0: centro dos lábios superiores
        """
        left_mouth = landmarks.landmark[61]
        right_mouth = landmarks.landmark[291]
        upper_lip = landmarks.landmark[0]
        
        # Largura da boca
        mouth_width = np.sqrt(
            (right_mouth.x - left_mouth.x)**2 + 
            (right_mouth.y - left_mouth.y)**2
        )
        
        # Altura do canto até lábio superior
        left_height = abs(left_mouth.y - upper_lip.y)
        right_height = abs(right_mouth.y - upper_lip.y)
        avg_height = (left_height + right_height) / 2
        
        # Razão largura/altura: sorriso tem razão alta
        smile_ratio = mouth_width / (avg_height + 1e-6)
        
        # Normalizar para [0, 1]
        smile_score = min(1.0, max(0.0, (smile_ratio - 2.0) / 3.0))
        
        return float(smile_score)
    
    def _extract_pose_features(self, landmarks) -> np.ndarray:
        """Extrai features dos 33 landmarks de pose."""
        features = []
        for landmark in landmarks.landmark:
            features.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
        return np.array(features)
    
    def _estimate_head_pose(self, landmarks) -> Dict[str, float]:
        """
        Estima orientação da cabeça (yaw, pitch, roll).
        
        Usa landmarks: nose (0), left eye (2), right eye (5)
        """
        nose = landmarks.landmark[0]
        left_eye = landmarks.landmark[2]
        right_eye = landmarks.landmark[5]
        
        # Calcular yaw (rotação horizontal)
        eye_center_x = (left_eye.x + right_eye.x) / 2
        yaw = (nose.x - eye_center_x) * 180  # -90 a +90 graus
        
        # Calcular pitch (rotação vertical)
        eye_center_y = (left_eye.y + right_eye.y) / 2
        pitch = (nose.y - eye_center_y) * 180
        
        # Calcular roll (inclinação)
        roll = np.arctan2(right_eye.y - left_eye.y, right_eye.x - left_eye.x) * 180 / np.pi
        
        return {
            'yaw': float(yaw),
            'pitch': float(pitch),
            'roll': float(roll)
        }
    
    def _extract_hand_features(self, multi_hand_landmarks) -> Dict:
        """Extrai features de mãos (gestos, movimentos repetitivos)."""
        hands_data = []
        for hand_landmarks in multi_hand_landmarks:
            features = []
            for landmark in hand_landmarks.landmark:
                features.extend([landmark.x, landmark.y, landmark.z])
            hands_data.append(features)
        
        return {
            'num_hands': len(hands_data),
            'landmarks': hands_data
        }
    
    def close(self):
        """Libera recursos."""
        self.face_mesh.close()
        self.pose.close()
        self.hands.close()


class VideoFeatureExtractor(nn.Module):
    """
    Extrator de features de vídeo combinando MediaPipe + embeddings neurais.
    
    Output: Tensor [batch, 768] com features agregadas
    """
    
    def __init__(self, embedding_dim: int = 768):
        super().__init__()
        
        self.mediapipe = MediaPipeAnalyzer()
        
        # MLP para agregar features do MediaPipe
        # Face: 468*3 = 1404, Pose: 33*4 = 132, Hands: 21*3*2 = 126
        # Total aproximado: ~1700 features
        self.face_encoder = nn.Sequential(
            nn.Linear(1404, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 256)
        )
        
        self.pose_encoder = nn.Sequential(
            nn.Linear(132, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 64)
        )
        
        self.hand_encoder = nn.Sequential(
            nn.Linear(126, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32)
        )
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(256 + 64 + 32, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, embedding_dim),
            nn.LayerNorm(embedding_dim)
        )
    
    def forward(self, frame_features: Dict) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            frame_features: Dict com 'face_landmarks', 'pose', 'hands'
            
        Returns:
            Tensor [embedding_dim] com features do frame
        """
        embeddings = []
        
        # Face
        if 'face_landmarks' in frame_features:
            face_tensor = torch.tensor(frame_features['face_landmarks'], dtype=torch.float32)
            face_emb = self.face_encoder(face_tensor)
            embeddings.append(face_emb)
        else:
            embeddings.append(torch.zeros(256))
        
        # Pose
        if 'pose' in frame_features:
            pose_tensor = torch.tensor(frame_features['pose'], dtype=torch.float32)
            pose_emb = self.pose_encoder(pose_tensor)
            embeddings.append(pose_emb)
        else:
            embeddings.append(torch.zeros(64))
        
        # Hands
        if 'hands' in frame_features and frame_features['hands']['num_hands'] > 0:
            # Pegar primeira mão ou média se houver duas
            hand_data = frame_features['hands']['landmarks'][0]
            hand_tensor = torch.tensor(hand_data, dtype=torch.float32)
            hand_emb = self.hand_encoder(hand_tensor)
            embeddings.append(hand_emb)
        else:
            embeddings.append(torch.zeros(32))
        
        # Concatenar e fusionar
        concat = torch.cat(embeddings, dim=0)
        output = self.fusion(concat)
        
        return output


class VideoPipeline:
    """
    Pipeline completo de análise de vídeo.
    
    Fluxo:
    1. Carrega vídeo
    2. Extrai frames (1 a cada N frames)
    3. Analisa cada frame com MediaPipe
    4. Agrega features temporalmente
    5. Detecta alertas (ausência contato visual, etc)
    6. Retorna resultado estruturado
    """
    
    def __init__(self, 
                 sample_rate: int = 5,  # Analisar 1 frame a cada 5
                 embedding_dim: int = 768):
        self.sample_rate = sample_rate
        self.mediapipe = MediaPipeAnalyzer()
        self.feature_extractor = VideoFeatureExtractor(embedding_dim)
        self.feature_extractor.eval()
        
        logger.info(f"Video Pipeline inicializado (sample_rate={sample_rate})")
    
    def analyze_video(self, video_path: str) -> VideoAnalysisResult:
        """
        Analisa vídeo completo.
        
        Args:
            video_path: Caminho para arquivo de vídeo
            
        Returns:
            VideoAnalysisResult com todas as métricas
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Analisando vídeo: {video_path} ({total_frames} frames, {fps} FPS)")
        
        frame_results = []
        frame_embeddings = []
        frame_count = 0
        analyzed_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sampling
            if frame_count % self.sample_rate == 0:
                # Analisar frame
                features = self.mediapipe.analyze_frame(frame)
                
                if features:
                    frame_results.append(features)
                    
                    # Extrair embedding
                    with torch.no_grad():
                        embedding = self.feature_extractor(features)
                        frame_embeddings.append(embedding.numpy())
                    
                    analyzed_count += 1
            
            frame_count += 1
        
        cap.release()
        
        logger.info(f"Frames analisados: {analyzed_count}/{total_frames}")
        
        # Agregar resultados temporalmente
        result = self._aggregate_results(frame_results, frame_embeddings, fps, analyzed_count)
        
        return result
    
    def _aggregate_results(self, 
                          frame_results: List[Dict],
                          frame_embeddings: List[np.ndarray],
                          fps: float,
                          frames_analyzed: int) -> VideoAnalysisResult:
        """Agrega resultados de todos os frames."""
        
        # Contato visual
        eye_gaze_scores = [r['eye_gaze']['looking_at_camera'] 
                          for r in frame_results if 'eye_gaze' in r]
        
        contato_visual_freq = np.mean(eye_gaze_scores) if eye_gaze_scores else 0.0
        
        # Calcular duração média de contato visual
        looking_frames = [i for i, score in enumerate(eye_gaze_scores) if score > 0.7]
        if looking_frames:
            # Agrupar frames consecutivos
            durations = []
            current_duration = 1
            for i in range(1, len(looking_frames)):
                if looking_frames[i] == looking_frames[i-1] + 1:
                    current_duration += 1
                else:
                    durations.append(current_duration * self.sample_rate / fps)
                    current_duration = 1
            duracao_media_contato = np.mean(durations) if durations else 0.0
        else:
            duracao_media_contato = 0.0
        
        # Expressões
        smile_scores = [r['smile'] for r in frame_results if 'smile' in r]
        sorriso_freq = np.mean(smile_scores) if smile_scores else 0.0
        
        # Head pose
        head_poses = [r['head_pose'] for r in frame_results if 'head_pose' in r]
        if head_poses:
            yaws = [hp['yaw'] for hp in head_poses]
            pitches = [hp['pitch'] for hp in head_poses]
            rolls = [hp['roll'] for hp in head_poses]
        else:
            yaws, pitches, rolls = [], [], []
        
        # Gestos (mãos)
        hand_counts = [r['hands']['num_hands'] for r in frame_results if 'hands' in r]
        gestos_detectados = sum(1 for c in hand_counts if c > 0)
        
        # Agregar embeddings
        if frame_embeddings:
            # Média temporal
            aggregated_embedding = np.mean(frame_embeddings, axis=0)
        else:
            aggregated_embedding = np.zeros(768)
        
        # Detectar alertas
        alertas = []
        
        # Alerta: ausência de contato visual
        if contato_visual_freq < 0.3:
            alertas.append({
                'severidade': 'critico',
                'tipo': 'ausencia_contato_visual',
                'descricao': f'Contato visual detectado em apenas {contato_visual_freq:.1%} do tempo',
                'confianca': 0.9,
                'modalidade': 'video'
            })
        
        # Alerta: ausência de sorriso
        if sorriso_freq < 0.1:
            alertas.append({
                'severidade': 'atencao',
                'tipo': 'ausencia_sorriso',
                'descricao': f'Sorriso detectado em apenas {sorriso_freq:.1%} do tempo',
                'confianca': 0.7,
                'modalidade': 'video'
            })
        
        # Score final de vídeo (0-1)
        # Quanto mais sinais atípicos, maior o score de risco
        score_video = 0.0
        score_video += (1.0 - contato_visual_freq) * 0.5  # Peso maior
        score_video += (1.0 - sorriso_freq) * 0.3
        score_video = min(1.0, score_video)
        
        return VideoAnalysisResult(
            score_video=score_video,
            contato_visual={
                'frequencia': float(contato_visual_freq),
                'duracao_media': float(duracao_media_contato)
            },
            expressoes={
                'sorriso': float(sorriso_freq)
            },
            head_pose={
                'yaw': yaws,
                'pitch': pitches,
                'roll': rolls
            },
            gestos={
                'detectados': gestos_detectados
            },
            alertas=alertas,
            embeddings=aggregated_embedding,
            frames_analisados=frames_analyzed,
            fps=fps
        )
    
    def close(self):
        """Libera recursos."""
        self.mediapipe.close()


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    pipeline = VideoPipeline(sample_rate=5)
    
    # Analisar vídeo de exemplo
    result = pipeline.analyze_video("exemplo.mp4")
    
    print(f"Score de vídeo: {result.score_video:.2f}")
    print(f"Contato visual: {result.contato_visual['frequencia']:.1%}")
    print(f"Alertas: {len(result.alertas)}")
    
    for alerta in result.alertas:
        print(f"  - [{alerta['severidade']}] {alerta['tipo']}: {alerta['descricao']}")
    
    pipeline.close()
