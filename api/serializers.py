from rest_framework import serializers
from wagtail.images.api.fields import ImageRenditionField
from wagtail.rich_text import expand_db_html
from core.utils import get_file_type, get_fontawesome_file_icon

from noticias.models import NoticiasPage
class NoticiasPageSerializer(serializers.ModelSerializer):
    imagem_destaque = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True)
    body = serializers.SerializerMethodField()
    arquivos = serializers.SerializerMethodField()

    class Meta:
        model = NoticiasPage
        fields = [
            'id', 'title', 'subtitle', 'descricao', 'data_publicacao', 'tags', 
            'imagem_destaque', 'url', 'body', 'destaque', 'arquivos'
        ]

    def get_body(self, obj):
        """Renderiza o StreamField 'body' como HTML."""
        if obj.body:
            return expand_db_html(obj.body.render_as_block())
        return ""

    def get_imagem_destaque(self, obj):
        imagem = obj.get_imagem_destaque()
        if imagem:
            request = self.context.get('request')
            return request.build_absolute_uri(imagem.get_rendition('fill-800x450').url)
        return None

    def get_arquivos(self, obj):
        """
        Serializa a lista de arquivos, incluindo URL absoluta e ícone.
        """
        arquivos_list = []
        if obj.arquivos:
            request = self.context.get('request')
            for block in obj.arquivos:
                arquivo = block.value
                file_info = get_file_type(arquivo)
                arquivos_list.append({
                    'title': arquivo.title,
                    'url': request.build_absolute_uri(arquivo.url),
                    'icon_class': get_fontawesome_file_icon(file_info)
                })
        return arquivos_list

class SharedContentSerializer(serializers.Serializer):
    SERIALIZERS = {
        NoticiasPage: NoticiasPageSerializer,
    }

    def to_representation(self, instance):
        model_class = type(instance)
        serializer_class = self.SERIALIZERS.get(model_class)

        if serializer_class:
            return serializer_class(instance, context=self.context).data
        return {
            'id': instance.id,
            'title': instance.title,
            'url': instance.url,
            'detail': 'Serializer específico não implementado para este tipo de conteúdo.'
        }