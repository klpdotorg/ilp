import logging

from django.views.decorators.cache import cache_page
from django.conf import settings

from rest_framework.views import APIView

from common.state_code_dict import STATE_CODES
from boundary.models import Boundary, BoundaryHierarchy

logger = logging.getLogger(__name__)

class CacheMixin(APIView):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(CacheMixin, cls).as_view(**initkwargs)

        if settings.CACHE_ENABLED:
            return cache_page(settings.CACHE_TIMEOUT)(view)
        return view


class ILPStateMixin(object):

    def get_state(self):
        state_code =  self.request.query_params.get('state', None)
        print("State code passed in via args is: ", state_code)
        state_name = STATE_CODES.get(state_code, None)
        print("State code translates to: ", state_name)
        state = Boundary.objects.get(
            name__iexact=state_name, boundary_type__name='State')
        return state

    def get_state_boundaries(self):
        state_code = self.request.query_params.get('state', None)
        print("State code passed in via args is: ", state_code)
        state_name = STATE_CODES.get(state_code, None)
        print("State code translates to: ", state_name)
        state = Boundary.objects.get(
            name__iexact=state_name, boundary_type__name='State')
        return BoundaryHierarchy.objects.filter(admin0_id=state.id)
