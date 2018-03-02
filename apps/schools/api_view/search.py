from boundary.models import Boundary, ElectionBoundary
from urllib.parse import urlparse 
from common.views import ILPAPIView
from django.core.urlresolvers import resolve, Resolver404
from rest_framework.response import Response
from schools.serializers import LeanInstitutionSummarySerializer
from boundary.serializers import (
        BoundarySerializer,
        ElectionBoundarySerializer)


class MergeEndpoints(ILPAPIView):
    """Merges multiple endpoint outputs
    E.g. - /merge?endpoints=/schMergeEndpointsools/school/33312/infrastructure&endpoints=/schools/school/33312/library
    merges output of both infrastructure and library endpoints and returns a single JSON.

    Keyword arguments:
    endpoints -- first endpoint
    endpoints -- second endpoint
    """
    def get(self, request, format=None):
        endpoints = request.GET.getlist('endpoints', [])
        data = {}
        if not endpoints:
            return Response({
                'error': 'no endpoints specified'
            }, status=404)

        for endpoint in endpoints:
            parsed = urlparse(endpoint)
            try:
                view, args, kwargs = resolve(parsed.path)
                kwargs['request'] = request._request
                data[endpoint] = view(*args, **kwargs).data
            except Exception as e:
                print(e)
                continue

        return Response(data, status=200)

class OmniSearch(ILPAPIView):
    """Omni-search endpoint for plain text search of all the entities

    Keyword arguments:
    text -- A string to search all kinds of entities for
    """
    is_omni = True

    def get(self, request, format=None):
        response = {
            'pre_schools': [],
            'primary_schools': [],
            'boundaries': [],
            'assemblies': [],
            'parliaments': [],
            'pincodes': [],
        }

        context = {
            'request': request,
            'view': self
        }

        params = request.QUERY_PARAMS
        text = params.get('text', '')

        if not text:
            return Response({
                'error': 'A text must be provided to search'
            }, status=404)

        response['pre_schools'] = LeanInstitutionSummarySerializer(
            Institution.objects.filter(
                (Q(name__icontains=text) | Q(id__contains=text)
                    | Q(dise__school_code__contains=text)),
                Q(status='AC'),
                Q(coord__isnull=False),
                Q(institution_type__name='Preschool')
            ).select_related(
                'coord',
                'institution_type',
                'address'
            )[:3],
            many=True,
            context=context
        ).data

        response['primary_schools'] = LeanInstitutionSummarySerializer(
            Institution.objects.filter(
                (Q(name__icontains=text) | Q(id__contains=text)
                    | Q(dise__school_code__contains=text)),
                Q(status='AC'),
                Q(coord__isnull=False),
                Q(institution_type__name='Primary School')
            ).select_related(
                'coord',
                'institution_type',
                'address'
            )[:3],
            many=True,
            context=context
        ).data

        response['boundaries'] = BoundarySerializer(
            Boundary.objects.filter(
                status='AC',
                name__icontains=text,
                geom__isnull=False
            ).select_related(
                'geom',
                'parent__name'
            ).prefetch_related('parent', 'boundaryhierarchy')[:10],
            many=True,
            context=context
        ).data

        response['assemblies'] = ElectionBoundarySerializer(
            ElectionBoundary.objects.filter(const_ward_type='MLA').filter(
                const_ward_name__icontains=text,
                geom__isnull=False
            )[:10],
            many=True,
            context=context
        ).data

        response['parliaments'] = ElectionBoundarySerializer(
            ElectionBoundary.objects.filter(const_ward_type='MP').filter(
                const_ward_name__icontains=text,
                geom__isnull=False
            )[:10],
            many=True,
            context=context
        ).data

        # response['pincodes'] = PincodeSerializer(
        #     Postal.objects.filter(
        #         pincode__icontains=text,
        #         coord__isnull=False
        #     )[:10],
        #     many=True,
        #     context=context
        # ).data

        return Response(response)