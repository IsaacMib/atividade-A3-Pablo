# 📚 Índice Mestre - Documentação NEUROATHENA

Bem-vindo à documentação do **NEUROATHENA** - Plataforma de Triagem Precoce de TEA com IA Multimodal.

---

## 🚀 Início Rápido

- **[01_GUIA_RAPIDO.md](./01_GUIA_RAPIDO.md)** - Instalação e primeiros passos
- **[INICIO_RAPIDO.md](./INICIO_RAPIDO.md)** - Configuração de ambiente (legado)

---

## 📐 Arquitetura e Estrutura

- **[03_ARQUITETURA/estrutura_site.md](./03_ARQUITETURA/estrutura_site.md)** - Estrutura completa do site
- **[ARQUITETURA.md](./ARQUITETURA.md)** - Visão geral da arquitetura técnica
- **[Estrutura.md](./Estrutura.md)** - Documento de planejamento completo

---

## 💻 Desenvolvimento

- **[DESENVOLVIMENTO.md](./DESENVOLVIMENTO.md)** - Guia para desenvolvedores
- **[logout-sso-wagtail.md](./logout-sso-wagtail.md)** - Configuração SSO/Logout

---

## 🏗️ Planejamento e Status

- **[PLANEJAMENTO.md](./PLANEJAMENTO.md)** - Roadmap e fases do projeto
- **[STATUS.md](./STATUS.md)** - Status atual de desenvolvimento
- **[AUDITORIA-PROJETO.md](./AUDITORIA-PROJETO.md)** - Auditoria técnica

---

## 📦 Estrutura de Apps Django

### Apps Principais
- **core/** - Modelos base, utilitários e configurações
- **home/** - Páginas institucionais (landing, sobre, contato)
- **blocks/** - Blocos Wagtail reutilizáveis (StreamField)
- **noticias/** - Sistema de blog/notícias
- **triagem_ia/** - Sistema de triagem com IA
- **painel_diario/** - Painel diário para famílias
- **profissionais/** - Dashboard para profissionais
- **comunidade/** - Recursos comunitários
- **lgpd/** - Compliance e privacidade

### IA Multimodal (Athena)
- **athena-ai/** - Sistema de IA multimodal
  - `video_model/` - Análise facial (MediaPipe, InsightFace)
  - `audio_model/` - Análise de prosódia (Wav2Vec2, Silero VAD)
  - `text_model/` - NLP (BERT, BERTimbau)
  - `multimodal_fusion/` - Fusão de modalidades (CLIP, ImageBind)
  - `api/` - API FastAPI

---

## 🎨 Frontend

- **frontend/js/** - JavaScript (Webpack, Babel)
- **frontend/scss/** - Estilos SCSS
- **frontend/img/** - Imagens e ícones

---

## 🔧 Configuração

- **requirements.txt** - Dependências Python do Django
- **athena-ai/requirements.txt** - Dependências da IA
- **package.json** - Dependências JavaScript
- **docker-compose.yml** - Configuração Docker
- **.env.example** - Variáveis de ambiente

---

## 📝 Branding

- **Master Brand**: LUMIPSYCHE (luz + psique)
- **Plataforma**: NEUROATHENA
- **IA**: Athena (Deusa da sabedoria e estratégia)

---

## 🆘 Suporte

Para dúvidas técnicas:
1. Consulte a documentação específica nos links acima
2. Verifique os issues no repositório
3. Entre em contato com a equipe de desenvolvimento

---

**Última atualização**: Novembro 2025  
**Versão**: 1.0.0
