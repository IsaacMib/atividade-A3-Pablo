# Agenda Recorrente - Sistema Otimizado

## Visão Geral

A funcionalidade de Agenda Recorrente permite criar compromissos que se repetem automaticamente em intervalos regulares **sem criar múltiplas páginas físicas no banco de dados**. O sistema usa uma abordagem lógica e otimizada onde uma única página pode representar múltiplas datas através de recorrência virtual.

## Como Usar

### 1. Criando uma Agenda com Recorrência

1. Acesse o admin do Wagtail
2. Navegue até uma página do tipo `AgendaPage`
3. Clique em "Adicionar página filha"
4. Selecione "Agenda do Dia"
5. Preencha os campos necessários

### 2. Campos Disponíveis

#### Configuração Básica
- **Data da Agenda**: Data inicial do compromisso
- **Compromissos do Dia**: Compromissos que serão aplicados nas datas de recorrência
- **Nome da Autoridade**: Nome padrão da autoridade (herdado do pai se não preenchido)
- **Local padrão**: Local padrão dos compromissos (herdado do pai se não preenchido)

#### Configuração da Recorrência
- **Habilitar recorrência**: Checkbox para ativar a funcionalidade de recorrência
- **Tipo de recorrência**: 
  - Sem recorrência (padrão)
  - Recorrência por dias
  - Recorrência por meses
  - Recorrência por anos
- **Intervalo de recorrência**: Quantidade de dias/meses/anos entre cada ocorrência
- **Data final da recorrência**: Data limite (opcional - deixe em branco para recorrência indefinida)

### 3. Exemplos de Uso

#### Reunião Semanal
- **Habilitar recorrência**: ✓ Marcado
- **Tipo**: Recorrência por dias
- **Intervalo**: 7
- **Data da agenda**: 2025-11-11 (segunda-feira)
- **Data final**: 2025-12-30

Resultado: Aplica os compromissos todas as segundas-feiras até o final do ano.

#### Reunião Mensal
- **Habilitar recorrência**: ✓ Marcado
- **Tipo**: Recorrência por meses
- **Intervalo**: 1
- **Data da agenda**: 2025-11-01
- **Data final**: (em branco)

Resultado: Aplica os compromissos no primeiro dia de cada mês indefinidamente.

#### Evento Anual
- **Habilitar recorrência**: ✓ Marcado
- **Tipo**: Recorrência por anos
- **Intervalo**: 1
- **Data da agenda**: 2025-12-25
- **Data final**: (em branco)

Resultado: Aplica os compromissos anualmente no Natal.

## Funcionamento Técnico Otimizado

### Lógica Virtual
O sistema **NÃO cria múltiplas páginas** no banco de dados. Em vez disso:

1. **Uma única página** representa todos os compromissos recorrentes
2. **Cálculo dinâmico** determina se uma data específica se aplica à recorrência
3. **Consultas inteligentes** retornam compromissos baseados na data solicitada
4. **Performance otimizada** sem sobrecarga de dados desnecessários

### Métodos Principais

#### `data_aplica_na_recorrencia(data_consulta)`
Verifica se uma data específica se encaixa na recorrência configurada.

#### `get_proximas_datas_recorrencia(data_inicio, limite)`
Calcula e retorna as próximas datas válidas baseadas na recorrência.

#### `get_agendas_para_data(data_consulta, parent_page)`
Método de classe que retorna todas as agendas (incluindo recorrentes) que se aplicam a uma data específica.

### API Atualizada

A rota `/dia/YYYY-MM-DD/` da `AgendaPage` agora:

1. Aceita qualquer data no formato YYYY-MM-DD
2. Busca automaticamente agendas com recorrência que se aplicam àquela data
3. Retorna todos os compromissos combinados de múltiplas agendas se necessário
4. Inclui informação sobre quantas agendas contribuíram para o resultado

## Vantagens da Nova Abordagem

### 1. Performance
- **Menos dados no banco**: Uma página representa infinitas datas
- **Consultas mais rápidas**: Não precisa buscar em milhares de registros
- **Menor uso de storage**: Economia significativa de espaço

### 2. Flexibilidade
- **Alterações centralizadas**: Mudar uma agenda afeta todas as recorrências
- **Configuração dinâmica**: Pode alterar recorrência sem recriar dados
- **Consulta por qualquer data**: Sistema calcula automaticamente

### 3. Manutenibilidade
- **Menos complexidade**: Não precisa gerenciar criação/exclusão em massa
- **Backup menor**: Menos dados para backup e restore
- **Migrações simples**: Mudanças de schema afetam menos registros

## Integração com Sistema Existente

A funcionalidade mantém **100% compatibilidade** com o sistema existente:

- Agendas sem recorrência funcionam normalmente
- Templates existentes continuam funcionando
- APIs mantêm o mesmo formato de resposta
- Hooks do Wagtail continuam operando

## Interface de Usuário

### Admin
- Campos organizados logicamente com a checkbox de habilitação
- Validações que impedem configurações inválidas
- Mensagens informativas sobre próximas ocorrências

### Template
- Mostra informações de recorrência quando habilitada
- Lista próximas 10 datas para visualização
- Mantém a mesma estrutura visual existente

## Limitações e Proteções

- **Máximo de datas calculadas**: 1000 por consulta (proteção contra loop)
- **Data limite padrão**: Cálculos não passam de 2050
- **Validação de dados**: Data final deve ser posterior à inicial
- **Fallback seguro**: Em caso de erro, trata como agenda normal