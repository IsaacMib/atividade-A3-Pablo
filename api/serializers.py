from rest_framework import serializers
from wagtail.images.api.fields import ImageRenditionField

class SharedContentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    summary = serializers.SerializerMethodField()
    publish_date = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()

    def get_summary(self, obj):
        return getattr(obj, 'descricao', getattr(obj, 'subtitle', ''))

    def get_publish_date(self, obj):
        return getattr(obj, 'data_publicacao', obj.first_published_at)

    def get_content_type(self, obj):
        return obj.specific_class._meta.model_name

    def get_absolute_url(self, obj):
        if request := self.context.get('request'):
            return obj.get_full_url(request=request)
        return obj.get_url()

    def get_featured_image(self, obj):
        image = None
        if hasattr(obj, 'get_imagem_destaque') and callable(obj.get_imagem_destaque):
            image = obj.get_imagem_destaque()
        if image:
            return ImageRenditionField('fill-800x450').to_representation(image)
        return None