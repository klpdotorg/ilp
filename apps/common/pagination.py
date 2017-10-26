from django.conf import settings

from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class ILPPaginationSerializer(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    page_size = settings.LARGESETPAGINATION
    page_size_query_param = 'page_size'
    max_page_size = settings.LARGESETPAGINATION
