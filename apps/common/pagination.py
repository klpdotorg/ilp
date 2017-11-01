from django.conf import settings

from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class ILPPaginationSerializer(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        print("Data in get_paginated_response is: ", data)
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })


class TestPagination(PageNumberPagination):
    
    def get_paginated_response(self, data):
        print("Data in get_paginated_response is: ", data)
        per_page = self.request.query_params.get("per_page")
        if per_page is not None:
            return Response({
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'count': self.page.paginator.count,
                'results': data
            })
        else:
            return Response({
                'results': data
            })

    def get_page_size(self, request):
        print("Inside get_page_size")
        per_page = request.query_params.get("per_page")
        if per_page is not None:
            print("per_page is Not NONE")
            page_size = request.query_params.get(self.page_size_query_param,                self.page_size)
            print("Page size is: ", page_size)
            if page_size > 0:
                return page_size
            elif page_size == 0:
                return None
            else:
                return None
        else:
            print("per_page is NONE")
            return None
        


class LargeResultsSetPagination(PageNumberPagination):
    page_size = settings.LARGESETPAGINATION
    page_size_query_param = 'page_size'
    max_page_size = settings.LARGESETPAGINATION
