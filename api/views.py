from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from taggit.models import Tag

from .serializers import SharedContentSerializer

try:
    from noticias.models import NoticiasPage
except ImportError:
    NoticiasPage = None

def _get_consistent_datetime(obj):
    from django.utils import timezone

    date_val = getattr(obj, 'data_publicacao', None)
    if date_val is None:
        date_val = obj.first_published_at
    
    if isinstance(date_val, datetime.date) and not isinstance(date_val, datetime.datetime):
        return timezone.make_aware(datetime.datetime(date_val.year, date_val.month, date_val.day, 0, 0, 0))
        
    return date_val


class SharedContentByTagAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    CONTENT_TYPE_MAP = {
        'noticias': NoticiasPage,
    }

    def get(self, request, tag_slug, format=None):
        try:
            tag = Tag.objects.get(slug=tag_slug)
        except Tag.DoesNotExist:
            return Response({"error": "Tag não encontrada"}, status=404)

        requested_types = [key for key in self.CONTENT_TYPE_MAP if request.query_params.get(key, 'false').lower() == 'true']
        if not requested_types:
            requested_types = self.CONTENT_TYPE_MAP.keys()

        response_data = {}
        all_results = []

        for content_type_key in requested_types:
            model = self.CONTENT_TYPE_MAP.get(content_type_key)
            if model:
                queryset = model.objects.live().public().filter(tags=tag).order_by('-first_published_at')

                if settings.API_CONTEUDO_AGRUPADO:
                    serializer = SharedContentSerializer(queryset, many=True, context={'request': request})
                    response_data[content_type_key] = serializer.data
                else:
                    all_results.extend(list(queryset))

        if settings.API_CONTEUDO_AGRUPADO:
            return Response(response_data)
        else:
            all_results.sort(key=_get_consistent_datetime, reverse=True)
            serializer = SharedContentSerializer(all_results, many=True, context={'request': request})
            return Response(serializer.data)


class AllSharedContentAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    CONTENT_TYPE_MAP = {
        'noticias': NoticiasPage,
    }

    def get(self, request, format=None):
        requested_types = [key for key in self.CONTENT_TYPE_MAP if request.query_params.get(key, 'false').lower() == 'true']
        if not requested_types:
            requested_types = self.CONTENT_TYPE_MAP.keys()

        all_results = []

        for content_type_key in requested_types:
            model = self.CONTENT_TYPE_MAP.get(content_type_key)
            if model:
                queryset = model.objects.live().public().order_by('-first_published_at')
                all_results.extend(list(queryset))

        all_results.sort(key=_get_consistent_datetime, reverse=True)
        serializer = SharedContentSerializer(all_results, many=True, context={'request': request})
        return Response(serializer.data)
