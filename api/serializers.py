from rest_framework import serializers
from wagtail.images.api.fields import ImageRenditionField

from noticias.models import NoticiasPage
class NoticiasPageSerializer(serializers.ModelSerializer):
    imagem_destaque = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = NoticiasPage
        fields = [
            'id', 'title', 'subtitle', 'descricao', 'data_publicacao',
            'tags', 'imagem_destaque', 'url', 'body', 'destaque'
        ]

    def get_imagem_destaque(self, obj):
        imagem = obj.get_imagem_destaque()
        if imagem:
            request = self.context.get('request')
            return request.build_absolute_uri(imagem.get_rendition('fill-800x450').url)
        return None

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