# Reestruturação: Site Padrão CODATA → NeuroPrev Multimodal

**Data**: 24 de novembro de 2025  
**Status**: ✅ Estrutura Base Concluída

---

## 📋 Resumo da Reestruturação

O projeto foi completamente reestruturado de um sistema de portais governamentais (Site Padrão CODATA-PB) para uma plataforma de **triagem precoce de autismo com IA multimodal** (NeuroPrev Multimodal).

---

## ✅ O que foi feito

### 1. Remoção de Apps Governamentais

Apps removidos completamente:
- ❌ `agenda/` - Agendas governamentais
- ❌ `avisos/` - Avisos institucionais
- ❌ `eventos/` - Eventos
- ❌ `editais/` - Editais públicos
- ❌ `intranet/` - Intranet governamental
- ❌ `dicas_presidente/` - Conteúdo específico
- ❌ `linhasdotempo/` - Linhas do tempo
- ❌ `institucional/` - Páginas institucionais antigas
- ❌ `documentos/` - Gestão de documentos
- ❌ `treinamento/` - Sistema de treinamento
- ❌ `contatos/` - Contatos governamentais
- ❌ `paginas/` - Sistema de páginas genéricas
- ❌ `plone_migration/` - Migração de Plone
- ❌ `auth_keycloak/` - Autenticação Keycloak
- ❌ `tw/` - Tailwind (não usado)

### 2. Apps Novos Criados

#### 🧠 `triagem/` - Core do Sistema
- **Models criados:**
  - `Crianca` - Dados da criança
  - `Triagem` - Registro de triagem multimodal
  - `QuestionarioResposta` - M-CHAT, Q-CHAT, etc.
  - `RelatorioLivre` - Relatos dos pais
  - `MidiaTriagem` - Imagens, vídeos, áudios

- **Funcionalidades:**
  - Análise multimodal (texto, imagem, vídeo, áudio)
  - Cálculo de risco estimado
  - Perfil comportamental em JSON
  - Orientações personalizadas

#### 📊 `painel_diario/` - Registro Diário
- Estrutura criada (a ser desenvolvido)
- Objetivo: Registro diário de humor, sono, alimentação, comportamentos

#### 👥 `comunidade/` - Comunidade para Pais
- Estrutura criada (a ser desenvolvido)
- Objetivo: Rede social segura para troca de experiências

#### 👨‍⚕️ `profissionais/` - Área Profissionais
- Estrutura criada (futuro)
- Objetivo: Dashboard para terapeutas e teleatendimento

#### 📚 `conteudo_educativo/` - CMS Wagtail
- Estrutura criada (a ser desenvolvido)
- Objetivo: Artigos educativos gerenciados pelo Wagtail

### 3. Apps Mantidos (Reutilizados)

- ✅ `home/` - Página inicial (será adaptada)
- ✅ `search/` - Busca
- ✅ `core/` - Utilitários centrais
- ✅ `blocks/` - Blocos Wagtail reutilizáveis
- ✅ `noticias/` - Blog/notícias (será adaptado)
- ✅ `lgpd/` - **ESSENCIAL** para dados de saúde
- ✅ `api/` - REST API

### 4. Configurações Atualizadas

#### `sitepadrao/settings/base.py`
- ✅ `INSTALLED_APPS` atualizado com novos apps
- ✅ `WAGTAIL_SITE_NAME` alterado para "NeuroPrev Multimodal"
- ✅ Referências antigas removidas

#### `README.md`
- ✅ Completamente reescrito
- ✅ Funcionalidades dos 6 módulos documentadas
- ✅ Arquitetura do sistema
- ✅ Roadmap de desenvolvimento
- ✅ Seção de segurança e LGPD
- ✅ Avisos legais

---

## 🚧 Próximos Passos

### Alta Prioridade (MVP)

1. **Migrations e Banco de Dados**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

2. **Models do Painel Diário**
   - `RegistroDiario` - Registro diário completo
   - `HumorDiario`, `SonoDiario`, `AlimentacaoDiario`
   - `ComportamentoDiario`, `CriseDiario`

3. **Models da Comunidade**
   - `PostComunidade` - Posts dos pais
   - `ComentarioComunidade` - Comentários
   - `GrupoComunidade` - Grupos temáticos

4. **Views e Templates**
   - Interface de cadastro de triagem
   - Formulários de questionários
   - Dashboard do painel diário
   - Feed da comunidade

5. **Admin Django**
   - Personalizar admin do `triagem/`
   - Criar inlines para questionários e mídias
   - Filtros e buscas otimizadas

### Média Prioridade

6. **Sistema de Questionários**
   - Implementar M-CHAT completo
   - Implementar Q-CHAT
   - Sistema de pontuação automatizado

7. **Upload de Mídias**
   - Sistema de upload de imagens
   - Sistema de upload de vídeos
   - Sistema de upload de áudios
   - Pré-processamento para IA

8. **API REST**
   - Endpoints de triagem
   - Endpoints de painel diário
   - Endpoints de comunidade
   - Documentação com Swagger

9. **Templates e Frontend**
   - Atualizar templates base
   - Remover branding CODATA
   - Criar identidade visual NeuroPrev
   - Adaptar CSS/SCSS

### Baixa Prioridade (Futuro)

10. **Integração com IA**
    - Modelo de análise de texto
    - Modelo de análise de imagem
    - Modelo de análise de vídeo
    - Modelo de análise de áudio
    - Fusão multimodal

11. **Sistema de Profissionais**
    - Dashboard para terapeutas
    - Teleatendimento
    - PTI (Plano Terapêutico Individual)

12. **Recursos Avançados**
    - Gráficos de evolução
    - Relatórios PDF
    - Notificações em tempo real
    - App mobile

---

## 📝 Checklist Técnico

### Backend
- [x] Apps governamentais removidos
- [x] Novos apps criados
- [x] Models de triagem criados
- [x] Admin básico criado
- [ ] Migrations executadas
- [ ] Models de painel_diario
- [ ] Models de comunidade
- [ ] Views implementadas
- [ ] URLs configuradas
- [ ] Testes unitários

### Frontend
- [ ] Templates base atualizados
- [ ] Branding CODATA removido
- [ ] Identidade visual NeuroPrev
- [ ] CSS/SCSS limpo
- [ ] JavaScript modularizado
- [ ] Testes Jest

### Infraestrutura
- [ ] Configurar banco PostgreSQL
- [ ] Configurar Redis
- [ ] Configurar armazenamento de mídia
- [ ] Configurar CI/CD
- [ ] Configurar ambiente de staging

### Segurança e LGPD
- [ ] Criptografia de dados sensíveis
- [ ] Sistema de consentimento
- [ ] Logs de auditoria
- [ ] Política de privacidade
- [ ] Termos de uso
- [ ] Direito ao esquecimento

---

## 🔧 Comandos Úteis

```bash
# Ambiente virtual
source .venv/bin/activate

# Migrations
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver

# Frontend
npm install
npm run build
npm run dev

# Testes
python manage.py test --keepdb
npm test
```

---

## 📊 Estatísticas

- **Apps Removidos**: 15
- **Apps Criados**: 5
- **Apps Mantidos**: 7
- **Models Criados**: 5 (triagem)
- **Lines Changed**: ~2000+
- **Tempo de Reestruturação**: ~2h

---

## 🎯 Objetivos do Projeto

1. **TCC**: Sistema funcional para trabalho de conclusão de curso
2. **Profissional**: Plataforma comercial viável
3. **Social**: Ferramenta gratuita para identificação precoce de TEA
4. **Científico**: Contribuir com pesquisa em IA aplicada à saúde

---

## 📚 Referências Mantidas

- Estrutura de testes (core/utils_test.py)
- Sistema de LGPD
- Blocks Wagtail reutilizáveis
- Configurações de ambiente (.tool-versions, .nvmrc)
- GitHub Copilot instructions

---

## ⚠️ Avisos Importantes

1. **Dados de Saúde**: Extremo cuidado com LGPD e segurança
2. **Não é Diagnóstico**: Sistema de triagem, não substitui avaliação profissional
3. **IA em Desenvolvimento**: Modelos multimodais ainda não implementados
4. **MVP First**: Focar em funcionalidades core antes de expandir

---

**Status Atual**: ✅ Estrutura base pronta para desenvolvimento  
**Próximo Marco**: MVP com questionários e painel diário básico
