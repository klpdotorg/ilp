from django.views.decorators.cache import cache_page
from django.conf import settings

from rest_framework.views import APIView

from common.state_code_dict import STATE_CODES
from boundary.models import Boundary


class CacheMixin(APIView):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(CacheMixin, cls).as_view(**initkwargs)

        if settings.CACHE_ENABLED:
            return cache_page(settings.CACHE_TIMEOUT)(view)
        return view


class ILPStateMixin(object):

    def get_state(self):
        state_code = self.kwargs.get('state', None)
        state_name = STATE_CODES.get(state_code, None)
        state = Boundary.objects.get(
            name__iexact=state_name, boundary_type__name='State')
        print("State is: ", state.name)
        return state
