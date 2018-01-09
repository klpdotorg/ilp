import logging

from django.views.decorators.cache import cache_page
from django.conf import settings
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.views import APIView
from common.state_code_dict import STATE_CODES
from boundary.models import (Boundary, BoundaryHierarchy, BoundaryStateCode)
from easyaudit.models import CRUDEvent
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class CompensationLogMixin(CreateModelMixin, UpdateModelMixin):
    def perform_create(self, serializer):
        logger.info("Inside compensationlog mixin")
        serializer.save(double_entry=1)

    def perform_update(self, serializer):
        print("Inside perform_update")
        user_who_created = CRUDEvent.objects.get(
            object_id=serializer.instance.id,
            event_type=CRUDEvent.CREATE
        ).user
        user_who_is_updating = self.request.user
        if user_who_is_updating == user_who_created:
            double_entry = 1
        else:
            double_entry = 2
        serializer.save(double_entry=double_entry)

class AnswerUpdateModelMixin(UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        print("inside update of answer update model mixin")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # data = self._cast_answer_types(request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CacheMixin(APIView):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(CacheMixin, cls).as_view(**initkwargs)

        if settings.CACHE_ENABLED:
            return cache_page(settings.CACHE_TIMEOUT)(view)
        return view


class ILPStateMixin(object):

    def get_state(self):
        state_code = self.request.query_params.get('state', None)
        # Once again, if no state is passed, default to 'ka'. 
        if state_code is None:
            state_code = 'ka'
        logger.debug("State code passed in via args is: ", state_code)
        state = None
        if state_code:
            state = BoundaryStateCode.objects.get(
                    char_id=state_code)
        return state.boundary

    def get_state_boundaries(self):
        state_code = self.request.query_params.get('state', None)
        logger.debug("State code passed in via args is: ", state_code)
        # Once again, if no state is passed, default to 'ka'. 
        if state_code is None:
            state_code = 'ka'
        boundaries = BoundaryHierarchy.objects.all()
        if state_code:
            state = BoundaryStateCode.objects.get(
                char_id=state_code)
            boundaries = boundaries.filter(admin0_id=state.boundary.id)
        return boundaries
