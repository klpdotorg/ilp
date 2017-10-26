from urllib.request import urlopen

from django.views.generic.base import TemplateView
from django.http import HttpResponse
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from common.pagination import ILPPaginationSerializer
from common.filters import ILPInBBOXFilter
from common.mixins import ILPStateMixin
from django.conf import settings


class StaticPageView(TemplateView):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(StaticPageView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context


class ILPAPIView(APIView):
    pass


class ILPViewSet(ILPStateMixin, ModelViewSet):
    
    pagination_serializer_class = ILPPaginationSerializer

    def __init__(self, *args, **kwargs):
        super(ILPViewSet, self).__init__(*args, **kwargs)
        if (
                hasattr(self, 'bbox_filter_field') and
                self.bbox_filter_field and
                ILPInBBOXFilter not in self.filter_backends
        ):
            self.filter_backends += (ILPInBBOXFilter,)


class ILPListAPIView(generics.ListAPIView):

    pagination_serializer_class = ILPPaginationSerializer

    def __init__(self, *args, **kwargs):
        super(ILPListAPIView, self).__init__(*args, **kwargs)
        if (
                hasattr(self, 'bbox_filter_field') and
                self.bbox_filter_field and
                ILPInBBOXFilter not in self.filter_backends
        ):
            self.filter_backends += (ILPInBBOXFilter,)

    def get_paginate_by(self):
        '''
            If per_page = 0, don't paginate.
            If format == csv, don't paginate.
        '''
        if self.request.accepted_renderer.format == 'csv':
            return None

        per_page = int(
            self.request.GET.get(
                'per_page', api_settings.ILPLISTVIEW_PAGE_SIZE
            )
        )
        if per_page == 0:
            return None
        return per_page


class ILPModelViewSet(viewsets.ModelViewSet):
    pass


class ILPDetailAPIView(generics.RetrieveAPIView):
    pass


class URLConfigView(APIView):

    def get(self):
        from ilp.api_urls import urlpatterns
        allowed_patterns = (
            'api_merge', 'api_school_info', 'api_donationuser_view'
        )

        patterns = []
        for pattern in urlpatterns:
            if pattern.name in allowed_patterns:
                patterns.append(
                    dict(name=pattern.name, pattern=pattern.regex.pattern)
                )
        return Response(dict(patterns=patterns))


class BlogFeedView(APIView):
    """ Returns blog entries packed into a JSON object """

    def get(self, request):
        url = settings.BLOG_FEED_URL
        json = urlopen(url).read()
        return HttpResponse(json)
