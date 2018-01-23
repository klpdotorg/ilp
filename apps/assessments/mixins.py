from django.conf import settings

from boundary.models import BoundaryStateCode


class AggQuerySetMixin(object):

    def get_queryset(self):
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        if institution_id:
            return self.institution_queryset.filter(
                institution_id=institution_id)
        if boundary_id:
            return self.boundary_queryset.objects.filter(
                boundary_id=boundary_id)

        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        return self.boundary_queryset.filter(boundary_id=state_id)
