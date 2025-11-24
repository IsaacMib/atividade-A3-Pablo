"""
Serviço de Integração Django ↔ FastAPI

Classe para consumir API de IA do Django e salvar resultados no banco.

Autor: NeuroPrev Team
Data: 2024-11-24
"""

import requests
from typing import Optional, Dict, List
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Serviço para consumir API de IA FastAPI."""
    
    def __init__(self, base_url: str = None):
        """
        Inicializa serviço.
        
        Args:
            base_url: URL base da API FastAPI (default: http://localhost:8001)
        """
        self.base_url = base_url or getattr(
            settings, 
            'AI_API_URL', 
            'http://localhost:8001'
        )
        self.timeout = 300  # 5 minutos para análises pesadas
    
    def health_check(self) -> Dict:
        """
        Verifica saúde da API.
        
        Returns:
            Dict com status e modelos carregados
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao verificar saúde da API: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analisa texto via API.
        
        Args:
            text: Texto para análise
        
        Returns:
            Dict com resultado da análise
        """
        try:
            response = requests.post(
                f"{self.base_url}/analyze/text",
                json={'text': text},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na análise de texto: {e}")
            raise
    
    def analyze_audio(self, audio_file: UploadedFile) -> Dict:
        """
        Analisa áudio via API.
        
        Args:
            audio_file: Arquivo de áudio Django UploadedFile
        
        Returns:
            Dict com resultado da análise
        """
        try:
            files = {
                'audio_file': (
                    audio_file.name,
                    audio_file.read(),
                    audio_file.content_type
                )
            }
            
            response = requests.post(
                f"{self.base_url}/analyze/audio",
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na análise de áudio: {e}")
            raise
    
    def analyze_video(self, video_file: UploadedFile) -> Dict:
        """
        Analisa vídeo via API.
        
        Args:
            video_file: Arquivo de vídeo Django UploadedFile
        
        Returns:
            Dict com resultado da análise
        """
        try:
            files = {
                'video_file': (
                    video_file.name,
                    video_file.read(),
                    video_file.content_type
                )
            }
            
            response = requests.post(
                f"{self.base_url}/analyze/video",
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na análise de vídeo: {e}")
            raise
    
    def analyze_multimodal(
        self,
        text: Optional[str] = None,
        audio_file: Optional[UploadedFile] = None,
        video_file: Optional[UploadedFile] = None
    ) -> Dict:
        """
        Análise multimodal completa.
        
        Args:
            text: Texto opcional
            audio_file: Arquivo de áudio opcional
            video_file: Arquivo de vídeo opcional
        
        Returns:
            Dict com resultado da fusão multimodal
        """
        try:
            # Preparar dados e arquivos
            data = {}
            files = {}
            
            if text:
                data['text'] = text
            
            if audio_file:
                files['audio_file'] = (
                    audio_file.name,
                    audio_file.read(),
                    audio_file.content_type
                )
            
            if video_file:
                files['video_file'] = (
                    video_file.name,
                    video_file.read(),
                    video_file.content_type
                )
            
            response = requests.post(
                f"{self.base_url}/analyze/multimodal",
                data=data,
                files=files if files else None,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na análise multimodal: {e}")
            raise


class TriagemAnalysisService:
    """Serviço para análise de triagem e salvamento no banco."""
    
    def __init__(self):
        """Inicializa serviço de triagem."""
        self.ai_service = AIAnalysisService()
    
    def analyze_triagem(self, triagem) -> Dict:
        """
        Analisa triagem completa (questionário + mídia).
        
        Args:
            triagem: Instância de Triagem model
        
        Returns:
            Dict com resultados salvos
        """
        from triagem_ia.models import ResultadoIA, AlertaIA
        
        logger.info(f"Iniciando análise de triagem #{triagem.id}")
        
        # 1. Preparar texto das respostas
        texto_respostas = self._prepare_respostas_text(triagem)
        
        # 2. Obter mídias (vídeo e áudio)
        video_file = self._get_video_file(triagem)
        audio_file = self._get_audio_file(triagem)
        
        # 3. Análise multimodal
        try:
            result = self.ai_service.analyze_multimodal(
                text=texto_respostas,
                video_file=video_file,
                audio_file=audio_file
            )
            
            # 4. Salvar ResultadoIA
            resultado_ia = ResultadoIA.objects.create(
                triagem=triagem,
                score_final=result['score_final'],
                nivel_risco=result['nivel_risco'],
                confianca=result['confianca'],
                scores_modalidades=result['scores_modalidades'],
                attention_weights=result['attention_weights'],
                principais_indicadores=result['principais_indicadores']
            )
            
            # 5. Criar alertas
            for recomendacao in result['recomendacoes']:
                AlertaIA.objects.create(
                    resultado=resultado_ia,
                    tipo='recomendacao',
                    severidade=self._map_severidade(result['nivel_risco']),
                    mensagem=recomendacao
                )
            
            # 6. Atualizar triagem
            triagem.nivel_risco = result['nivel_risco']
            triagem.status = 'concluida'
            triagem.save()
            
            logger.info(
                f"Análise de triagem #{triagem.id} concluída: "
                f"risco={result['nivel_risco']}, score={result['score_final']:.2f}"
            )
            
            return {
                'resultado_ia_id': resultado_ia.id,
                'nivel_risco': result['nivel_risco'],
                'score_final': result['score_final'],
                'confianca': result['confianca']
            }
        
        except Exception as e:
            logger.error(f"Erro na análise de triagem #{triagem.id}: {e}")
            triagem.status = 'erro'
            triagem.save()
            raise
    
    def _prepare_respostas_text(self, triagem) -> str:
        """Prepara texto das respostas do questionário."""
        from triagem_ia.models import RespostaQuestionario
        
        respostas = RespostaQuestionario.objects.filter(triagem=triagem).select_related('pergunta')
        
        texto_parts = []
        for resposta in respostas:
            pergunta_texto = resposta.pergunta.texto
            
            if resposta.resposta_texto:
                resposta_texto = resposta.resposta_texto
            elif resposta.resposta_sim_nao is not None:
                resposta_texto = "Sim" if resposta.resposta_sim_nao else "Não"
            elif resposta.resposta_numerica is not None:
                resposta_texto = str(resposta.resposta_numerica)
            else:
                continue
            
            texto_parts.append(f"{pergunta_texto}: {resposta_texto}")
        
        return "\n".join(texto_parts)
    
    def _get_video_file(self, triagem) -> Optional[UploadedFile]:
        """Obtém arquivo de vídeo da triagem."""
        # TODO: Implementar quando tiver modelo de MídiaTriagem
        return None
    
    def _get_audio_file(self, triagem) -> Optional[UploadedFile]:
        """Obtém arquivo de áudio da triagem."""
        # TODO: Implementar quando tiver modelo de MídiaTriagem
        return None
    
    def _map_severidade(self, nivel_risco: str) -> str:
        """Mapeia nível de risco para severidade de alerta."""
        mapping = {
            'baixo': 'info',
            'medio': 'warning',
            'alto': 'critico'
        }
        return mapping.get(nivel_risco, 'info')


class PainelDiarioAnalysisService:
    """Serviço para análise de mídia do painel diário."""
    
    def __init__(self):
        """Inicializa serviço de painel diário."""
        self.ai_service = AIAnalysisService()
    
    def analyze_midia(self, midia_registro):
        """
        Analisa mídia de registro diário.
        
        Args:
            midia_registro: Instância de MidiaRegistroDiario model
        
        Returns:
            Dict com análise salva
        """
        logger.info(f"Analisando mídia #{midia_registro.id} tipo={midia_registro.tipo}")
        
        try:
            if midia_registro.tipo == 'video':
                result = self.ai_service.analyze_video(midia_registro.arquivo)
                
                # Salvar análise
                midia_registro.analise_ia = {
                    'score_video': result['score_video'],
                    'contato_visual': result['contato_visual'],
                    'expressoes': result['expressoes'],
                    'alertas': result['alertas']
                }
            
            elif midia_registro.tipo == 'audio':
                result = self.ai_service.analyze_audio(midia_registro.arquivo)
                
                # Salvar análise
                midia_registro.analise_ia = {
                    'score_audio': result['score_audio'],
                    'prosody_atipica': result['prosody_atipica'],
                    'emocao_predominante': result['emocao_predominante'],
                    'alertas': result['alertas']
                }
            
            else:
                logger.warning(f"Tipo de mídia não suportado: {midia_registro.tipo}")
                return None
            
            midia_registro.save()
            
            logger.info(f"Análise de mídia #{midia_registro.id} concluída")
            
            return midia_registro.analise_ia
        
        except Exception as e:
            logger.error(f"Erro ao analisar mídia #{midia_registro.id}: {e}")
            raise


# Exemplo de uso
if __name__ == "__main__":
    # Health check
    service = AIAnalysisService()
    health = service.health_check()
    print(f"API Status: {health}")
    
    # Análise de texto
    text = "Meu filho não fala, não olha nos olhos e prefere ficar sozinho."
    result = service.analyze_text(text)
    print(f"Análise de texto: {result}")
