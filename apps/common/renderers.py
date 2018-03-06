from rest_framework.renderers import JSONRenderer
from rest_framework_csv.renderers import CSVRenderer


class ILPJSONRenderer(JSONRenderer):
    '''
        Sub-classes JSONRenderer to render GeoJSON where appropriate.
        If the request contains a geometry=yes parameter, it converts features
        to GeoJSON
    '''

    media_type = 'application/json'
    format = 'json'
    render_geometry = False

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Figure out whether we need to render geometry based on GET param
        render_geometry = renderer_context['request'].GET.get('geometry', 'no')
        status = renderer_context['response'].status_code

        # Only try and fetch geometries if response status is 200
        if render_geometry == 'yes' and status == 200:
            self.render_geometry = True
        # if data is a list, that means pagination was turned off
        # with per_page=0
        # then we first need to convert the list to a dict so that
        # we have same data structure:
        if isinstance(data, list):
            data = {
                'count': len(data),
                'results': data
            }

        # If the view is an "omni" view, we need to handle it differently
        is_omni = False
        if isinstance(data, dict):
            view = renderer_context['view']
            if hasattr(view, 'is_omni') and view.is_omni:
                is_omni = True

        # If geometry=yes and results are a list, convert to geojson
        if self.render_geometry and 'results' in data and \
                isinstance(data['results'], list):
            data['type'] = 'FeatureCollection'
            features = data.pop('results')
            data['features'] = [self.get_feature(elem) for elem in features]

        # If geometry=yes and is a single feature, convert data to geojson
        elif self.render_geometry and not is_omni:
            data = self.get_feature(data)

        elif self.render_geometry and is_omni:
            for key in data:
                arr = data[key]
                data[key] = {}
                data[key]['type'] = 'FeatureCollection'
                data[key]['features'] = [
                    self.get_feature(elem) for elem in arr]

        # If geometry=no, just convert data as is to JSON
        else:
            pass

        return super(ILPJSONRenderer, self).\
            render(data, accepted_media_type, renderer_context)

    def get_feature(self, elem):
        '''
            Passed an element with properties, including a 'geometry' property,
            will convert it to GeoJSON format
        '''
        # This should never be called if geometry=no
        if 'geometry' not in elem:
            geometry = {}
        else:
            geometry = elem.pop('geometry')

        feature = {
            'type': 'Feature',
            'geometry': geometry,
            'properties': elem
        }
        return feature

class KLPCSVRenderer(CSVRenderer):
    media_type = 'application/csv'
