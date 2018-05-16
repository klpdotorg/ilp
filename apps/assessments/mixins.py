from django.conf import settings

from boundary.models import BoundaryStateCode


class AggMixin(object):
    """
    - AggMixin is mainly used in GKA Aggregate Viewsets.
    - The inheriting class should have
    `institution_queryset` and `boundary_queryset` variables.
    - If the GET query is to look into institution/boundary this mixin helps
    to use the respective querysets.
    - If both instituion_id and boundary_id is not passed,
    uses boundary_queryset with state_id as boundary_id.
    """

    def get_queryset(self):
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        if institution_id:
            return self.institution_queryset.filter(
                institution_id=institution_id)
        if boundary_id:
            return self.boundary_queryset.filter(
                boundary_id=boundary_id)

        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        return self.boundary_queryset.filter(boundary_id=state_id)
