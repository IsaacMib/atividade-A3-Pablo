# 🏗️ Estrutura Completa do Site - NEUROATHENA

Hierarquia e organização de todas as páginas do site institucional.

---

## 🌳 Hierarquia de Páginas

```
📄 HomePage (/)
├── 📄 Sobre Nós (/sobre-nos/)
│   ├── História do LUMIPSYCHE
│   ├── Missão e Visão
│   ├── Equipe
│   └── Parcerias
│
├── 🧩 Para Famílias (/para-familias/)
│   ├── Por que NEUROATHENA?
│   ├── Como Funciona a Triagem
│   ├── Painel Diário
│   ├── Comunidade
│   ├── Recursos Educativos
│   └── FAQ para Pais
│
├── 🏥 Para Profissionais (/para-profissionais/)
│   ├── Suíte Clínica
│   ├── Dashboard Profissional
│   ├── API para Integração
│   ├── Estudos e Validação
│   └── Treinamento e Suporte
│
├── 🤖 IA Multimodal Athena (/ia-multimodal/)
│   ├── Como Funciona
│   ├── 4 Módulos de Análise
│   │   ├── Análise de Vídeo (Facial)
│   │   ├── Análise de Áudio (Prosódia)
│   │   ├── Análise de Texto (Linguagem)
│   │   └── Fusão Multimodal
│   ├── Precisão e Validação
│   ├── Ética e Privacidade
│   └── Publicações Científicas
│
├── 📰 Notícias e Blog (/noticias/)
│   ├── Artigos Educativos
│   ├── Atualizações do Sistema
│   ├── Estudos de Caso
│   └── Eventos
│
└── 📧 Contato (/contato/)
    ├── Formulário de Contato
    ├── Informações Institucionais
    └── Redes Sociais
```

---

## 📄 Detalhamento das Páginas

### 1. **HomePage** (`HomePage`)

**Tipo**: Página inicial principal  
**Template**: `home/home_page.html`  
**Blocos disponíveis**:
- Hero com vídeo/imagem de fundo
- Feature cards (3-4 destaques principais)
- Estatísticas (precisão IA, famílias atendidas, etc.)
- Depoimentos
- CTA para cadastro/triagem
- Últimas notícias

**Conteúdo sugerido**:
- Headline: "Detecção Precoce de TEA com IA Multimodal"
- Subheadline: "Triagem inteligente, acompanhamento diário, apoio contínuo"
- CTAs: "Iniciar Triagem Gratuita" | "Saiba Mais"

---

### 2. **Sobre Nós** (`SobreNosPage`)

**Tipo**: Página institucional  
**URL**: `/sobre-nos/`  
**Blocos disponíveis**:
- Hero com imagem institucional
- Rich text (história e missão)
- Timeline (marcos históricos do projeto)
- Estatísticas (impacto social)
- Imagem + Texto (equipe, parcerias)

**Seções**:
1. **História do LUMIPSYCHE** - Origem do projeto, motivação
2. **Missão e Visão** - Objetivos e valores
3. **Equipe** - Profissionais envolvidos (psicólogos, devs, IA)
4. **Parcerias** - Universidades, clínicas, institutos
5. **Diferenciais** - O que torna o NEUROATHENA único

---

### 3. **Para Famílias** (`ParaFamiliasPage`)

**Tipo**: Landing page para pais/cuidadores  
**URL**: `/para-familias/`  
**Blocos disponíveis**:
- Hero específico para famílias
- Feature cards (4 benefícios principais)
- Timeline (jornada do usuário: cadastro → triagem → acompanhamento)
- FAQ para pais
- Depoimentos de famílias
- CTA para cadastro

**Seções**:
1. **Por que NEUROATHENA?**
   - Detecção precoce aumenta eficácia do tratamento
   - Ferramenta validada cientificamente
   - Gratuita e acessível

2. **Como Funciona a Triagem**
   - Passo 1: Cadastro (5 min)
   - Passo 2: Questionário + vídeo (15 min)
   - Passo 3: Análise da IA Athena (instantâneo)
   - Passo 4: Relatório e recomendações

3. **Painel Diário**
   - Registro de comportamentos
   - Marcos de desenvolvimento
   - Gráficos e evolução
   - Compartilhamento com profissionais

4. **Comunidade**
   - Fórum de pais
   - Grupos de apoio
   - Eventos e webinars

5. **Recursos Educativos**
   - Biblioteca de conteúdo sobre TEA
   - Vídeos explicativos
   - Guias práticos

---

### 4. **Para Profissionais** (`ParaProfissionaisPage`)

**Tipo**: Landing page para clínicos  
**URL**: `/para-profissionais/`  
**Blocos disponíveis**:
- Hero profissional
- Feature cards (ferramentas da suíte clínica)
- Imagem + Texto (casos de uso)
- Estatísticas (precisão, validação)
- CTA para cadastro profissional

**Seções**:
1. **Suíte Clínica NEUROATHENA**
   - Dashboard centralizado
   - Gestão de pacientes
   - Histórico e evolução
   - Relatórios automatizados

2. **Dashboard Profissional**
   - Visualização de triagens
   - Anotações clínicas
   - Agendamento
   - Integração com prontuários

3. **API para Integração**
   - Integração com sistemas existentes
   - Webhooks e notificações
   - Documentação técnica

4. **Estudos e Validação**
   - Publicações científicas
   - Métricas de precisão
   - Comparação com métodos tradicionais

5. **Treinamento e Suporte**
   - Onboarding para profissionais
   - Webinars técnicos
   - Suporte dedicado

---

### 5. **IA Multimodal Athena** (`IAMultimodalPage`)

**Tipo**: Página explicativa técnica  
**URL**: `/ia-multimodal/`  
**Blocos disponíveis**:
- Hero com conceito de IA
- Feature cards (4 módulos de análise)
- Imagem + Texto (explicação técnica)
- Estatísticas (precisão por módulo)
- FAQ técnica

**Seções**:
1. **Como Funciona a Athena**
   - Visão geral da arquitetura multimodal
   - Fluxo de dados: entrada → análise → fusão → resultado

2. **4 Módulos de Análise**
   
   **a) Análise de Vídeo (Facial)**
   - MediaPipe, InsightFace
   - Detecção de expressões faciais
   - Rastreamento de contato visual
   - Análise de emoções
   
   **b) Análise de Áudio (Prosódia)**
   - Silero VAD, Wav2Vec2
   - Análise de prosódia (entonação, ritmo)
   - Detecção de padrões de fala atípicos
   - Ecolalia e repetições
   
   **c) Análise de Texto (Linguagem)**
   - BERT, BERTimbau (português)
   - Processamento de respostas textuais
   - Análise semântica
   - Detecção de padrões linguísticos
   
   **d) Fusão Multimodal**
   - CLIP, ImageBind
   - Combinação inteligente das 4 modalidades
   - Score de confiança unificado
   - Explicabilidade dos resultados

3. **Precisão e Validação**
   - Datasets utilizados
   - Métricas (sensibilidade, especificidade, AUC)
   - Comparação com métodos tradicionais (MCHAT, ADOS)
   - Validação clínica

4. **Ética e Privacidade**
   - LGPD compliance
   - Criptografia de dados
   - Anonimização
   - Transparência algorítmica
   - Não substituição do diagnóstico clínico

---

### 6. **Notícias e Blog** (`NoticiasIndexPage` + `NoticiasPage`)

**Tipo**: Sistema de blog  
**URL**: `/noticias/`  
**Funcionalidades**:
- Listagem de posts por data
- Categorias e tags
- Busca de conteúdo
- Compartilhamento social
- Comentários (opcional)

**Tipos de conteúdo**:
1. **Artigos Educativos** - TEA, desenvolvimento infantil
2. **Atualizações do Sistema** - Novos recursos, melhorias
3. **Estudos de Caso** - Histórias reais de sucesso
4. **Eventos** - Webinars, palestras, workshops
5. **Pesquisas** - Publicações científicas da equipe

---

### 7. **Contato** (`ContatoPage`)

**Tipo**: Formulário de contato (AbstractEmailForm)  
**URL**: `/contato/`  
**Campos do formulário**:
- Nome completo
- Email
- Telefone (opcional)
- Tipo de contato (dropdown):
  - Dúvidas sobre triagem
  - Suporte técnico
  - Parcerias institucionais
  - Imprensa
  - Outro
- Mensagem

**Informações exibidas**:
- Email institucional: contato@neuroathena.com.br
- Telefone: (XX) XXXX-XXXX
- Endereço (se aplicável)
- Redes sociais (links)
- Horário de atendimento

---

## 🔐 Páginas Autenticadas (Futuro)

Estas páginas requerem login e estão fora do escopo institucional:

```
🔒 Área Logada
├── 📊 Dashboard Família
│   ├── Minha Conta
│   ├── Triagens Realizadas
│   ├── Painel Diário
│   └── Relatórios
│
├── 🏥 Dashboard Profissional
│   ├── Meus Pacientes
│   ├── Triagens Pendentes
│   ├── Relatórios Clínicos
│   └── Configurações
│
└── 👥 Comunidade
    ├── Fórum
    ├── Grupos
    ├── Mensagens
    └── Eventos
```

---

## 🎨 Blocos StreamField por Página

| Página | Blocos Recomendados |
|--------|---------------------|
| HomePage | Hero, FeatureCards, Statistics, Testimonial, CTA |
| SobreNosPage | Hero, RichText, Timeline, ImageText, Statistics |
| ParaFamiliasPage | Hero, FeatureCards, Timeline, FAQ, Testimonial |
| ParaProfissionaisPage | Hero, FeatureCards, ImageText, Statistics, CTA |
| IAMultimodalPage | Hero, FeatureCards, RichText, ImageText, FAQ |

---

## 📱 Responsividade

Todas as páginas devem ser **mobile-first** e responsivas:
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

---

## 🌐 SEO e Acessibilidade

- Títulos únicos por página (< 60 caracteres)
- Meta descriptions (< 160 caracteres)
- Alt text em todas as imagens
- Hierarquia de headings (H1 → H2 → H3)
- ARIA labels em elementos interativos
- Contraste WCAG AA mínimo (4.5:1)

---

## 🚀 Próximas Fases

1. **Fase 1**: Implementar páginas institucionais ✅
2. **Fase 2**: Criar templates HTML para blocos
3. **Fase 3**: Adicionar SCSS e frontend interativo
4. **Fase 4**: Implementar área logada (dashboard)
5. **Fase 5**: Integração com Athena IA

---

**Referência**: Ver [Estrutura.md](../Estrutura.md) para visão completa do projeto.
