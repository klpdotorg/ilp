from common.models import Language
from rest_framework import generics
from common.serializers import LanguageSerializer


class LanguagesListView(generics.ListAPIView):
    serializer_class = LanguageSerializer
    paginator = None

    def get_queryset(self):
        return Language.objects.all()

