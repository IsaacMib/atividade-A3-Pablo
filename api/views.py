from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from taggit.models import Tag

from .serializers import SharedContentSerializer

try:
    from noticias.models import NoticiasPage
except ImportError:
    NoticiasPage = None

try:
    from avisos.models import AvisosPage
except ImportError:
    AvisosPage = None



class SharedContentByTagAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    CONTENT_TYPE_MAP = {
        'noticias': NoticiasPage,
        'avisos': AvisosPage,
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
            all_results.sort(key=lambda x: getattr(x, 'data_publicacao', x.first_published_at), reverse=True)
            serializer = SharedContentSerializer(all_results, many=True, context={'request': request})
            return Response(serializer.data)
