from wagtail.blocks import StructBlock, ListBlock, FloatBlock, CharBlock
import requests
import json
import time

# Cache simples em memória
_metabase_cache = {}
_CACHE_TIMEOUT = 600  # 10 minutos em segundos

class OdometerBlock(StructBlock):
    # Campos não editáveis pelo usuário
    odometer_description = CharBlock(required=True, max_length=100, label="Descrição do Dado")
    odometer_value = FloatBlock(required=False, label="Valor do Dado Default", help_text="Preenchido automaticamente pela API", disabled=True)
    id_card = CharBlock(required=True, label="ID do Card do Metabase")

    def get_context(self, value, parent_context=None):
        from django.conf import settings
        context = super().get_context(value, parent_context=parent_context)
        id_card = value['id_card']
        url = f"{settings.METABASE_API_URL}{id_card}"
        headers = {
          'x-api-key': settings.METABASE_API_KEY
        }
        cache_key = f"metabase_{id_card}"
        now = time.time()
        # Verifica cache
        if cache_key in _metabase_cache:
            cached = _metabase_cache[cache_key]
            if now - cached['timestamp'] < _CACHE_TIMEOUT:
                data = cached['data']
            else:
                del _metabase_cache[cache_key]
                data = None
        else:
            data = None
        if data is None:
            try:
                response = requests.get(url, headers=headers)
                data = response.json() if response.ok else {}
                _metabase_cache[cache_key] = {'data': data, 'timestamp': now}
            except Exception as e:
                data = {'error': str(e)}
        context['metabase_data'] = data.get('result_metadata', {})
        result_metadata = data.get('result_metadata', [])
        if result_metadata:
            # Atualiza apenas o valor com os dados da API
            context['self'].metabase_value = result_metadata[0].get('fingerprint', {}).get('type', {}).get('type/Number',{}).get('q1', 0)
        else:
            context['self'].metabase_value = 0
        context['id_card'] = id_card
        return context

    class Meta:
        template = 'blocks/odometer.html'
        icon = 'plus'
        label = 'Odometer'

class OdometerListBlock(StructBlock):
    odometers = ListBlock(OdometerBlock(), label="Central de Monitoramento Detran")

    class Meta:
        template = 'blocks/central_monitoramento_detran.html'
        icon = 'list-ul'
        label = 'Central de Monitoramento Detran'
