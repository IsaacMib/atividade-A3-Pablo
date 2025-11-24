# NeuroPrev Multimodal - Planejamento de Desenvolvimento

**Sistema de Triagem Precoce de Autismo com IA Multimodal**

---

## 📅 Cronograma MVP (TCC) - 16 Semanas

### SPRINT 1-2: Fundação e Estrutura (Semanas 1-2)

**Objetivo**: Criar base técnica sólida do projeto

#### Tarefas:

- [x] Limpar código governamental do template base
- [x] Configurar ambiente de desenvolvimento
- [x] Atualizar logos e identidade visual
- [x] Documentar arquitetura completa
- [ ] Criar apps Django principais:
  - [ ] `triagem_ia/` - Módulo de triagem
  - [ ] `painel_diario/` - Registro diário
  - [ ] `comunidade/` - Rede social
  - [ ] `biblioteca_conteudos/` - Conteúdos educativos
- [ ] Configurar PostgreSQL para produção
- [ ] Configurar Celery + Redis para tarefas assíncronas
- [ ] Setup de testes automatizados

**Entregáveis:**
- ✅ Projeto limpo e documentado
- Apps principais criados com estrutura básica
- Testes rodando (pytest + coverage)

---

### SPRINT 3-4: Autenticação e Perfis (Semanas 3-4)

**Objetivo**: Sistema de usuários completo e seguro

#### Tarefas:

- [ ] **Criar User Model customizado**
  ```python
  # core/models.py
  class Usuario(AbstractUser):
      tipo_usuario = models.CharField(choices=[
          ('responsavel', 'Responsável'),
          ('profissional', 'Profissional'),
          ('admin', 'Administrador'),
      ])
      telefone = models.CharField(max_length=20)
      data_nascimento = models.DateField(null=True)
      aceite_termos = models.BooleanField(default=False)
      data_aceite_termos = models.DateTimeField(null=True)
  ```

- [ ] **Sistema de Onboarding**
  - Cadastro com validação de email
  - Termo de consentimento LGPD
  - Questionário inicial (dados da criança)
  - Tutorial do sistema

- [ ] **Perfis**
  - PerfilResponsavel (dados pessoais + crianças)
  - PerfilProfissional (CRP/CRFa + especialidade) - futuro
  - PerfilPai (comunidade)

- [ ] **Autenticação**
  - Login/Logout
  - Recuperação de senha
  - Troca de senha
  - Autenticação em duas etapas (2FA) - opcional

- [ ] **Permissões**
  - Grupos: responsavel, profissional, moderador, admin
  - Permissões customizadas por módulo

**Entregáveis:**
- Sistema de cadastro/login funcional
- Onboarding completo com LGPD
- Perfis configuráveis

---

### SPRINT 5-7: Módulo de Triagem (Semanas 5-7)

**Objetivo**: Core do sistema - triagem multimodal MVP

#### Tarefas Semana 5:

- [ ] **Modelos de Dados**
  - Questionario, Pergunta, Triagem, RespostaQuestionario
  - ModalidadeTexto, ResultadoIA, AlertaIA
  - Migrations completas

- [ ] **Questionários Estruturados**
  - Implementar M-CHAT-R (20 perguntas)
  - Implementar Q-CHAT (25 perguntas)
  - Questionário de desenvolvimento geral
  - Histórico perinatal
  - Validações de formulário

#### Tarefas Semana 6:

- [ ] **Interface de Triagem**
  - Wizard multi-etapas (questionários)
  - Progresso visual
  - Salvamento automático (draft)
  - Campo de relato livre
  - Preview antes de enviar

- [ ] **API de Triagem**
  ```python
  # triagem_ia/api/views.py
  POST   /api/triagem/criar/           # Iniciar triagem
  POST   /api/triagem/{id}/responder/  # Enviar respostas
  POST   /api/triagem/{id}/analisar/   # Processar com IA
  GET    /api/triagem/{id}/resultado/  # Obter resultado
  ```

#### Tarefas Semana 7:

- [ ] **Análise de IA - Versão MVP (Baseada em Regras)**
  ```python
  # triagem_ia/ia/analisador.py
  
  class AnalisadorTriagemMVP:
      """
      Versão MVP: Análise baseada em regras validadas
      (Versão com ML será implementada em FASE 2)
      """
      
      def calcular_score_mchat(self, respostas):
          # Pontuação M-CHAT-R (0-20)
          # Pontos de corte: 
          # 0-2: Baixo risco
          # 3-7: Risco moderado
          # 8+: Alto risco
          pass
      
      def analisar_texto_nlp(self, relato):
          # NLP básico com spaCy ou NLTK
          # Detectar palavras-chave:
          # - "não responde", "não olha", "repetitivo"
          # - "atraso", "regressão", "ecolalia"
          pass
      
      def gerar_resultado(self, triagem):
          # Combinar scores
          # Gerar nível de risco
          # Criar recomendações personalizadas
          pass
  ```

- [ ] **Processamento Assíncrono**
  ```python
  # triagem_ia/tasks.py (Celery)
  
  @shared_task
  def processar_triagem(triagem_id):
      triagem = Triagem.objects.get(id=triagem_id)
      analisador = AnalisadorTriagemMVP()
      resultado = analisador.gerar_resultado(triagem)
      # Salvar ResultadoIA
      # Criar AlertaIA se necessário
      # Enviar email com resultado
  ```

- [ ] **Página de Resultado**
  - Visualização do nível de risco
  - Gráfico de perfil comportamental
  - Sinais identificados
  - Recomendações personalizadas
  - Botão de exportar PDF

**Entregáveis Sprint 5-7:**
- ✅ Questionários M-CHAT-R e Q-CHAT funcionais
- ✅ Análise MVP com regras + NLP básico
- ✅ Resultado completo com recomendações
- ✅ Processamento assíncrono (Celery)

---

### SPRINT 8-10: Painel Diário (Semanas 8-10)

**Objetivo**: Registro diário e análise temporal

#### Tarefas Semana 8:

- [ ] **Modelos de Dados**
  - Crianca, RegistroDiario, MidiaRegistroDiario
  - TipoTerapia, SessaoTerapia
  - Migrations

- [ ] **Interface de Registro Diário**
  - Formulário amigável (mobile-first)
  - Emojis para humor
  - Escalas visuais (1-5 estrelas)
  - Upload de foto/vídeo/áudio
  - Observações livres

#### Tarefas Semana 9:

- [ ] **Histórico e Evolução**
  - Linha do tempo de registros
  - Filtros por período
  - Comparação entre semanas
  - Busca em observações

- [ ] **Gráficos de Evolução**
  ```javascript
  // Usar Chart.js ou D3.js
  - Humor ao longo do tempo (line chart)
  - Qualidade do sono (bar chart)
  - Frequência de crises (scatter plot)
  - Evolução de terapias (progress bars)
  ```

#### Tarefas Semana 10:

- [ ] **Análise Temporal com IA**
  ```python
  # painel_diario/ia/analisador_temporal.py
  
  @shared_task
  def analisar_evolucao_semanal(crianca_id):
      # Comparar última semana com anterior
      # Detectar padrões:
      # - Regressão (piora em múltiplos indicadores)
      # - Avanço (melhora consistente)
      # - Gatilhos de crises (correlação com eventos)
      # Gerar AlertaIA se detectar regressão
      pass
  ```

- [ ] **Alertas Automáticos**
  - "Criança teve 3 crises esta semana (acima da média)"
  - "Qualidade do sono piorou 40% em relação ao mês passado"
  - "Detectada regressão na linguagem - considere consultar terapeuta"

- [ ] **Lembretes**
  - Notificação diária para registrar
  - Lembrete de sessão de terapia
  - Sugestão de atualização de triagem (a cada 3 meses)

**Entregáveis Sprint 8-10:**
- ✅ Registro diário funcional
- ✅ Gráficos de evolução
- ✅ Alertas automáticos de regressão
- ✅ Análise temporal básica

---

### SPRINT 11-13: Comunidade (Semanas 11-13)

**Objetivo**: Rede social segura para pais

#### Tarefas Semana 11:

- [ ] **Modelos de Dados**
  - PerfilPai, Grupo, Postagem, Comentario
  - ReacaoPostagem, ConteudoProfissional, Moderacao
  - Migrations

- [ ] **Feed e Postagens**
  - Feed público
  - Criar postagem (texto + foto)
  - Categorias (relato, dúvida, conquista, desabafo)
  - Comentários
  - Reações (apoio, obrigado, força, parabéns)

#### Tarefas Semana 12:

- [ ] **Grupos Temáticos**
  - Criar grupo
  - Entrar em grupo
  - Feed do grupo
  - Notificações de grupo
  - Tipos: Faixa etária, Terapia, Região

- [ ] **Sistema de Moderação**
  - Filtro de palavras proibidas
  - Denúncia de postagens/comentários
  - Fila de moderação para admins
  - Log de ações de moderação

#### Tarefas Semana 13:

- [ ] **Conteúdos Profissionais**
  - Área especial para profissionais verificados
  - Publicar artigos/dicas
  - Categorias: Orientação, Exercício, Dica, Artigo
  - Biblioteca de conteúdos

- [ ] **Notificações**
  - Notificação de comentário
  - Notificação de reação
  - Notificação de nova postagem no grupo
  - Centro de notificações

**Entregáveis Sprint 11-13:**
- ✅ Feed de postagens funcional
- ✅ Grupos temáticos
- ✅ Sistema de moderação
- ✅ Conteúdos profissionais

---

### SPRINT 14-15: CMS Wagtail e Conteúdo (Semanas 14-15)

**Objetivo**: Área pública institucional completa

#### Tarefas:

- [ ] **Páginas Wagtail**
  - HomePage atualizada (hero, destaques, como funciona)
  - NoticiaIndexPage + NoticiaPage
  - ArtigoIndexPage + ArtigoPage
  - BibliotecaPage (recursos educativos)
  - SobrePage (sobre o projeto, equipe, pesquisa)
  - ContatoPage (formulário)
  - PoliticasPage (Termos, Privacidade, LGPD)

- [ ] **Conteúdo Inicial**
  - 5 artigos sobre TEA
  - 3 notícias sobre o projeto
  - 10 recursos na biblioteca (PDFs, vídeos, checklists)
  - Página Sobre completa

- [ ] **SEO e Acessibilidade**
  - Meta tags otimizadas
  - Schema.org markup
  - Alt text em imagens
  - Contraste WCAG AA
  - Navegação por teclado

**Entregáveis Sprint 14-15:**
- ✅ Site público completo
- ✅ Conteúdo inicial publicado
- ✅ SEO otimizado

---

### SPRINT 16: Testes, Deploy e Apresentação (Semana 16)

**Objetivo**: Finalizar MVP para apresentação do TCC

#### Tarefas:

- [ ] **Testes Finais**
  - Coverage mínimo 70% em todos os apps
  - Testes de integração (fluxos completos)
  - Testes de performance (load testing básico)
  - Testes de segurança (OWASP básico)

- [ ] **Deploy em Produção**
  - Configurar servidor (DigitalOcean/AWS/Heroku)
  - PostgreSQL configurado
  - Celery + Redis funcionando
  - S3 para mídia
  - HTTPS configurado
  - Backup automático

- [ ] **Documentação Final**
  - README completo
  - Guia do Usuário
  - Documentação da API
  - Apresentação para TCC (slides)
  - Artigo científico (se aplicável)

- [ ] **Dados de Demonstração**
  - Criar usuários de teste
  - Triagens de exemplo
  - Registros diários simulados
  - Postagens na comunidade

**Entregáveis Sprint 16:**
- ✅ Sistema em produção
- ✅ Documentação completa
- ✅ Apresentação do TCC pronta

---

## 📊 Métricas de Sucesso MVP

### Funcionais:
- ✅ Usuário consegue fazer triagem completa (M-CHAT-R + Q-CHAT)
- ✅ IA retorna resultado em < 30 segundos
- ✅ Registro diário leva < 2 minutos para preencher
- ✅ Gráficos de evolução carregam em < 3 segundos
- ✅ Comunidade permite criar postagem e comentar

### Técnicas:
- ✅ Coverage de testes ≥ 70%
- ✅ Performance: carregamento de página < 2s
- ✅ Zero erros críticos em produção
- ✅ Uptime ≥ 99% (após deploy)

### Científicas:
- ✅ Resultado de triagem baseado em instrumentos validados (M-CHAT-R, Q-CHAT)
- ✅ Análise textual com NLP identifica palavras-chave relevantes
- ✅ Sistema gera alertas para regressão de comportamento

---

## 🚀 FASE 2: Multimodalidade (Pós-TCC)

### Sprints 17-24: Análise de Imagem/Vídeo

- [ ] Treinar modelo de Computer Vision
  - Dataset: Fotos de crianças com TEA (ético e anonimizado)
  - Detectar: Contato visual, expressões faciais, gestos
  - Framework: TensorFlow ou PyTorch

- [ ] Implementar upload de vídeo
  - Análise frame-by-frame
  - Detectar movimentos repetitivos
  - Resposta a estímulos

### Sprints 25-32: Análise de Áudio

- [ ] Treinar modelo de Speech Analysis
  - Dataset: Áudios de crianças com TEA
  - Analisar: Prosódia, ritmo, ecolalia
  - Framework: Librosa + TensorFlow

### Sprints 33-40: Fusão Multimodal

- [ ] Implementar Ensemble Model
  - Combinar predições de 4 modalidades
  - Pesos ajustáveis por modalidade
  - Calibração de probabilidades

---

## 🎓 Estrutura da Apresentação do TCC

### Slide 1: Título
- NeuroPrev Multimodal
- Sistema de Triagem Precoce de Autismo com IA Multimodal

### Slide 2: Problema
- TEA afeta 1 em cada 36 crianças (CDC, 2023)
- Diagnóstico tardio (média: 4-5 anos)
- Intervenção precoce (antes dos 3 anos) melhora prognóstico

### Slide 3: Solução Proposta
- Plataforma de triagem com IA
- Acompanhamento familiar diário
- Comunidade de apoio

### Slide 4: Base Científica
- Pesquisa: "A multimodular approach..."
- Instrumentos validados: M-CHAT-R, Q-CHAT

### Slide 5: Arquitetura do Sistema
- Diagrama técnico (Django + Wagtail + IA)

### Slide 6: Módulos Implementados
- Triagem Multimodal
- Painel Diário
- Comunidade
- CMS Educativo

### Slide 7: Demonstração
- Vídeo ou live demo

### Slide 8: Resultados e Métricas
- Testes realizados
- Performance
- Feedback de usuários beta

### Slide 9: LGPD e Segurança
- Conformidade total
- Criptografia
- Direitos do titular

### Slide 10: Roadmap Futuro
- Multimodalidade completa
- App mobile
- Profissionalização

### Slide 11: Conclusão e Impacto
- Impacto social esperado
- Contribuição científica

---

## 📝 Checklist Final (Semana 16)

### Funcionalidades:
- [ ] Cadastro/Login funcionando
- [ ] Onboarding completo
- [ ] Triagem M-CHAT-R + Q-CHAT
- [ ] Resultado com IA
- [ ] Registro diário
- [ ] Gráficos de evolução
- [ ] Alertas de regressão
- [ ] Feed da comunidade
- [ ] Grupos temáticos
- [ ] Moderação
- [ ] CMS público
- [ ] Exportar dados (LGPD)

### Técnico:
- [ ] Testes ≥ 70% coverage
- [ ] Deploy em produção
- [ ] HTTPS configurado
- [ ] Celery funcionando
- [ ] Backup automático
- [ ] Logs configurados
- [ ] Monitoramento (Sentry)

### Documentação:
- [ ] README completo
- [ ] ARQUITETURA.md
- [ ] Guia do Usuário (PDF)
- [ ] API docs (Swagger/ReDoc)
- [ ] Apresentação TCC (slides)
- [ ] Artigo científico (opcional)

### Deploy:
- [ ] Domínio registrado (ex: neuroprev.com.br)
- [ ] SSL/TLS ativo
- [ ] Email configurado
- [ ] CDN configurado (Cloudflare)
- [ ] Backup semanal automático

---

## 🎯 Próximos Passos IMEDIATOS

### Esta Semana:

1. **Criar apps principais**
   ```bash
   python manage.py startapp triagem_ia
   python manage.py startapp painel_diario
   python manage.py startapp comunidade
   python manage.py startapp biblioteca_conteudos
   ```

2. **Configurar PostgreSQL**
   - Instalar PostgreSQL
   - Criar banco de dados
   - Atualizar settings.py

3. **Configurar Celery + Redis**
   - Instalar Redis
   - Configurar Celery
   - Criar primeira task

4. **Criar modelos iniciais**
   - Usuario customizado
   - ConsentimentoLGPD
   - LogAcesso

5. **Setup de testes**
   - Configurar pytest
   - Criar testes iniciais
   - Configurar coverage

---

*Última atualização: 24/11/2025*
