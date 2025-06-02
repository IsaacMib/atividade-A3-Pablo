from wagtail.blocks import StructBlock, ListBlock, FloatBlock, CharBlock
import requests
import json
from django.core.cache import cache

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
        data = cache.get(cache_key)
        if data is None:
            try:
                response = requests.get(url, headers=headers)
                data = response.json() if response.ok else {}
                cache.set(cache_key, data, timeout=_CACHE_TIMEOUT)
            except Exception as e:
                data = {'error': str(e)}
        context['metabase_data'] = data.get('result_metadata', {})
        result_metadata = data.get('result_metadata', [])
        if result_metadata:
            # Atualiza apenas o valor com os dados da API
            context['self'].metabase_value = result_metadata[0].get('fingerprint', {}).get('type', {}).get('type/Number',{}).get('q1', 0)
        else:
            context['self'].metabase_value = value['odometer_value'] # Valor default se não houver dados
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
