# Sistema de Banner Personalizado

## Visão Geral

O novo sistema de banners permite **personalização completa** de tamanhos e modos de renderização usando o sistema de **Wagtail Renditions**. Substituímos o antigo sistema de 5 proporções fixas por **67 tamanhos pré-definidos** e **4 modos de renderização**.

---

## Modos de Renderização

### 1. **Fill** (Preencher)
- Redimensiona e **corta** a imagem para preencher exatamente o tamanho especificado
- Mantém o aspect ratio e corta as partes que excedem
- **Uso recomendado**: Banners hero, cards de grid, thumbnails
- **Exemplo**: `fill-1920x1080` → Imagem sempre será exatamente 1920x1080px

### 2. **Max** (Máximo)
- Redimensiona a imagem para **caber dentro** do tamanho especificado
- Mantém aspect ratio original, nunca corta
- Pode resultar em dimensões menores que as especificadas
- **Uso recomendado**: Imagens com bordas importantes, logos, ilustrações
- **Exemplo**: `max-1920x1080` → Imagem de 2000x1000 vira 1920x960px

### 3. **Min** (Mínimo)
- Redimensiona para que pelo menos **uma dimensão** atinja o tamanho especificado
- Mantém aspect ratio, pode exceder em uma dimensão
- **Uso recomendado**: Backgrounds que precisam cobrir área completa
- **Exemplo**: `min-1920x1080` → Imagem sempre cobrirá toda área

### 4. **Original**
- Usa a imagem original **sem modificações**
- Ignora o tamanho especificado
- **Uso recomendado**: SVGs, imagens já otimizadas, controle total
- **Exemplo**: `original` → Imagem mantém suas dimensões originais

---

## Tamanhos Disponíveis

### 🔹 **Ícones** (quadrados pequenos)
```
16x16, 32x32, 48x48, 64x64, 96x96, 128x128
```
**Uso**: Favicons, ícones de app, avatares pequenos

### 🔹 **Thumbnails** (quadrados médios)
```
200x200, 300x300, 400x400, 500x500, 600x600, 800x800, 1000x1000, 1150x1150
```
**Uso**: Miniaturas de produtos, avatares grandes, previews

### 🔹 **Horizontais - HD/FHD**
```
Básicos:
- 128x85, 480x320, 640x427, 800x533, 1024x683

HD (720p):
- 1280x720, 1280x853, 1280x960

Full HD (1080p):
- 1920x1080, 1920x1280, 1920x1440
```
**Uso**: Banners hero, sliders, capas

### 🔹 **Horizontais - 2K/4K**
```
2K:
- 2560x1440, 2560x1707, 2560x1920

4K:
- 3840x2160, 3840x2560
```
**Uso**: Banners de alta qualidade, telas grandes, displays profissionais

### 🔹 **Verticais - Mobile/Stories**
```
Básicos:
- 480x640, 640x853, 800x1066

HD/FHD:
- 1080x1350, 1080x1440, 1080x1920

Especiais:
- 750x1334 (iPhone portrait)
- 1536x2048 (iPad portrait)
```
**Uso**: Stories, feeds mobile, banners verticais

### 🔹 **Ultrawides** (cinema/panorâmico)
```
- 2560x1080 (21:9)
- 3440x1440 (21:9)
- 3840x1080 (32:9)
- 5120x1440 (32:9)
```
**Uso**: Banners largos, headers panorâmicos, monitores ultrawide

---

## Como Usar no Admin

### Passo 1: Adicionar Banner
1. Vá para uma página que aceita banners
2. Clique em **"Adicionar Banner com Link"**
3. Faça upload da **imagem desktop** (obrigatória)
4. Faça upload da **imagem mobile** (opcional, mas recomendado)

### Passo 2: Escolher Modo e Tamanho
1. **Modo**: Escolha entre Fill/Max/Min/Original
2. **Tamanho**: Selecione o tamanho apropriado (ex: 1920x1080)

### Passo 3: Configurar Link
1. **Link**: URL de destino (ex: `/noticias/`)
2. **Alt Text**: Descrição acessível da imagem
3. **Nova Aba**: Marque para abrir link em nova aba

### Passo 4: Salvar e Visualizar
- Clique em **Salvar**
- Visualize a página para ver o banner aplicado
- **Staff verá badge** informativo com modo/tamanho no canto superior direito

---

## Exemplos de Uso

### Banner Hero Principal
```
Modo: Fill
Tamanho: 1920x1080
Imagem Desktop: hero-desktop.jpg (3000x2000px)
Imagem Mobile: hero-mobile.jpg (1080x1920px)
```
**Resultado**: Banner sempre 1920x1080, otimizado para desktop e mobile

### Banner com Logo
```
Modo: Max
Tamanho: 800x533
Imagem Desktop: logo-banner.png (1000x400px)
Imagem Mobile: logo-banner.png
```
**Resultado**: Logo mantém proporção, não corta bordas

### Background Completo
```
Modo: Min
Tamanho: 1920x1080
Imagem Desktop: background.jpg (2560x1440px)
```
**Resultado**: Imagem sempre cobre área completa do banner

### Imagem SVG
```
Modo: Original
Tamanho: (qualquer, será ignorado)
Imagem Desktop: ilustracao.svg
```
**Resultado**: SVG renderizado em tamanho original, vetorial

---

## Boas Práticas

### ✅ Imagens Desktop
- **Resolução mínima**: 1920x1080 para banners hero
- **Formato recomendado**: JPEG (fotos), PNG (gráficos/transparência)
- **Tamanho máximo**: 5MB (Wagtail otimiza automaticamente)

### ✅ Imagens Mobile
- **Sempre forneça** versão mobile para banners importantes
- **Formato vertical**: 1080x1350 ou 1080x1920 para stories
- **Formato horizontal**: 640x427 ou 800x533 para banners compactos

### ✅ Escolha do Modo
| Situação | Modo Recomendado |
|----------|------------------|
| Banner hero, cards | **Fill** |
| Logos, ilustrações | **Max** |
| Backgrounds | **Min** |
| SVGs, imagens pré-otimizadas | **Original** |

### ✅ Performance
- Wagtail **cacheia renditions** automaticamente
- Primeira renderização pode demorar, depois é instantânea
- Imagens são otimizadas server-side (qualidade 85% JPEG)

### ✅ Acessibilidade
- **Sempre preencha Alt Text** com descrição da imagem
- Use textos descritivos (não "banner1.jpg")
- Para imagens decorativas, use Alt Text vazio: `""`

---

## Arquitetura Técnica

### Estrutura do Block
```python
class BannerComLinkBlock(blocks.StructBlock):
    imagem = ImageChooserBlock(required=True)
    imagem_mobile = ImageChooserBlock(required=False)
    link = blocks.URLBlock(required=True)
    alt_texto = blocks.CharBlock(required=True)
    abrir_nova_aba = blocks.BooleanBlock(required=False)
    mode = blocks.ChoiceBlock(choices=[...])  # 4 opções
    size = blocks.ChoiceBlock(choices=[...])  # 67 opções
```

### Método get_context()
```python
def get_context(self, value, parent_context=None):
    context = super().get_context(value, parent_context)
    
    # Desktop rendition
    if value.get('imagem'):
        filter_spec = f"{value['mode']}-{value['size']}"
        context['rendition_desktop'] = imagem.get_rendition(filter_spec)
    
    # Mobile rendition (mesmo filtro)
    if value.get('imagem_mobile'):
        context['rendition_mobile'] = imagem_mobile.get_rendition(filter_spec)
    
    return context
```

### Template Simplificado
```django
<picture class="banner-picture">
  {% if rendition_mobile %}
    <source media="(max-width: 768px)" srcset="{{ rendition_mobile.url }}">
  {% endif %}
  
  {% if rendition_desktop %}
    <img src="{{ rendition_desktop.url }}" 
         alt="{{ self.alt_texto }}"
         width="{{ rendition_desktop.width }}"
         height="{{ rendition_desktop.height }}">
  {% endif %}
</picture>
```

### Badge Informativo (Staff Only)
```html
{% if request.user.is_staff %}
  <div class="banner-info-badge">
    <span class="badge-mode">{{ self.get_mode_display }}</span>
    <span class="badge-size">{{ self.size }}</span>
  </div>
{% endif %}
```

---

## Migração do Sistema Antigo

### Antes (5 proporções fixas)
```python
proporcao = blocks.ChoiceBlock(choices=[
    ('1-1', 'Quadrado'),
    ('3-2', 'Paisagem'),
    ('4-3', 'Clássico'),
    ('16-9', 'Wide'),
    ('18-6', 'Ultrawide'),
])
```

### Depois (flexível)
```python
mode = blocks.ChoiceBlock(choices=[...])  # fill/max/min/original
size = blocks.ChoiceBlock(choices=[...])  # 67 opções
```

### Equivalências Aproximadas
| Antiga Proporção | Nova Configuração |
|------------------|-------------------|
| 1-1 (Quadrado) | Fill + 800x800 |
| 3-2 (Paisagem) | Fill + 1280x853 |
| 4-3 (Clássico) | Fill + 1024x683 |
| 16-9 (Wide) | Fill + 1920x1080 |
| 18-6 (Ultrawide) | Fill + 1800x600 |

---

## Troubleshooting

### Imagem não aparece
- ✅ Verifique se `imagem` está preenchida (obrigatório)
- ✅ Confirme que modo e tamanho estão selecionados
- ✅ Veja console do navegador para erros 404

### Imagem cortada incorretamente
- Use **Max** ao invés de **Fill** para manter área completa
- Ajuste composição da imagem no upload
- Teste com diferentes tamanhos

### Performance lenta na primeira carga
- Normal! Wagtail gera rendition na primeira requisição
- Rendições subsequentes são cacheadas
- Para pré-gerar: `python manage.py wagtail_update_image_renditions`

### Badge não aparece
- Badge só é visível para **staff** (`request.user.is_staff`)
- Faça login no admin antes de visualizar

---

## Referências

- [Wagtail Images Documentation](https://docs.wagtail.org/en/stable/topics/images.html)
- [Wagtail Rendition Filters](https://docs.wagtail.org/en/stable/advanced_topics/images/renditions.html)
- Código fonte: `blocks/models.py` (BannerComLinkBlock)
- Template: `blocks/templates/blocks/banner.html`

---

**Última atualização**: Sistema implementado com 4 modos e 67 tamanhos pré-definidos  
**Status**: ✅ Produção (migration não necessária - StreamField usa JSON)
