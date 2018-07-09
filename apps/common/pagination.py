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


class ILPDefaultPagination(PageNumberPagination):
    
    def get_paginated_response(self, data):
        ''' This method determines the basic JSON structure of the response. 
        The output of this is passed onto the ILPJSONRenderer which then further formats the output to the desired format '''
        per_page = int(self.request.query_params.get(
            "per_page",
            settings.LARGESETPAGINATION))
        # length = None
        if isinstance(data, list):
            length = len(data)
            print("Size of data is: ", length)
        # If per_page is a number greater than zero, then
        # pagination is desired.
        if per_page > 0:
            return Response({
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'count': self.page.paginator.count,
                'results': data
            })
        # Pagination is not desired. Return everything in one shot
        else:
            return Response({
                    'results': data
            })
         

    def get_page_size(self, request):
        per_page = int(request.query_params.get(
            "per_page",
            settings.LARGESETPAGINATION))
        if per_page > 0:
            # return max(per_page, int(settings.LARGESETPAGINATION))
            return per_page
        elif per_page == 0:
            return None
        else:
            return settings.LARGESETPAGINATION


class LargeResultsSetPagination(PageNumberPagination):
    page_size = settings.LARGESETPAGINATION
    page_size_query_param = 'page_size'
    max_page_size = settings.LARGESETPAGINATION
