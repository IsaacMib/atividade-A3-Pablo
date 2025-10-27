from rest_framework import serializers
from wagtail.images.api.fields import ImageRenditionField
from wagtail.rich_text import expand_db_html
from django.conf import settings
from core.utils import get_file_type, get_fontawesome_file_icon

from noticias.models import NoticiasPage
class NoticiasPageSerializer(serializers.ModelSerializer):
    imagem_destaque = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True)
    body = serializers.SerializerMethodField()
    arquivos = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = NoticiasPage
        fields = [
            'id',
            'title',
            'subtitle',
            'descricao',
            'data_publicacao',
            'tags',
            'imagem_destaque',
            'url',
            'body',
            'destaque',
            'arquivos',
            'images',
            'slideshow_imagens', 
            'nao_exibir_lista_de_arquivos', 
        ]

    def get_body(self, obj):
        if obj.body:
            return expand_db_html(
                obj.body.render_as_block(
                    context={'request': self.context.get('request')}
                )
            )
        return ""

    def get_imagem_destaque(self, obj):
        imagem = obj.get_imagem_destaque()
        if imagem:
            request = self.context.get('request')
            rendition_url = imagem.get_rendition('fill-800x450').url
            if request:
                return request.build_absolute_uri(rendition_url)
            if hasattr(settings, 'WAGTAILADMIN_BASE_URL'):
                return f"{settings.WAGTAILADMIN_BASE_URL}{rendition_url}"
        return None

    def get_arquivos(self, obj):
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

    def get_images(self, obj):
        images_list = []
        if obj.images:
            request = self.context.get('request')
            for block in obj.images:
                if block.block_type == 'imagem' and block.value:
                    image_url = block.value.get_rendition('original').url
                    absolute_url = image_url
                    if request:
                        absolute_url = request.build_absolute_uri(image_url)
                    elif hasattr(settings, 'WAGTAILADMIN_BASE_URL'):
                        absolute_url = f"{settings.WAGTAILADMIN_BASE_URL}{image_url}"
                    images_list.append({
                        'url': absolute_url,
                        'title': block.value.title
                    })
        return images_list


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
