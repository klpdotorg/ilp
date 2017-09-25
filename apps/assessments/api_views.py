from common.views import ILPListAPIView
from common.utils import Date

from rest_framework.response import Response


class StoryMetaView(ILPListAPIView):

    def get(self, request):
        survey = self.request.query_params.get('survey', None)
        source = self.request.query_params.get('source', None)
        versions = self.request.query_params.getlist('version', None)
        admin1_id = self.request.query_params.get('admin1', None)
        admin2_id = self.request.query_params.get('admin2', None)
        admin3_id = self.request.query_params.get('admin3', None)
        school_id = self.request.query_params.get('school_id', None)
        mp_id = self.request.query_params.get('mp_id', None)
        mla_id = self.request.query_params.get('mla_id', None)
        start_date = self.request.query_params.get('from', None)
        end_date = self.request.query_params.get('to', None)
        school_type = self.request.query_params.get(
            'school_type', 'Primary School'
        )
        top_summary = self.request.query_params.get('top_summary', None)
        date = Date()

        response_json = {}
        return Response(response_json)
