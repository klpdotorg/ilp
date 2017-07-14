from rest_framework.test import APITestCase
import json
import base64
from django.urls import reverse
from django.contrib.auth import get_user_model
# Create your tests here.

from boundary.models import Boundary, BoundaryType
from common.models import Status, InstitutionType

class BoundaryApiTests(APITestCase):
    def setUp(self):

        #setup a test user
        self.user = get_user_model().objects.create_user('admin', 'admin@klp.org.in', 'admin')

        country, created = BoundaryType.objects.get_or_create(char_id="C", name="Country")
        state, created = BoundaryType.objects.get_or_create(char_id="ST", name="State")
        school_district, created = BoundaryType.objects.get_or_create(char_id="SD", name="School District")
        preschool_district, created = BoundaryType.objects.get_or_create(char_id="PD", name="Preschool District")


        active_status, created = Status.objects.get_or_create(char_id="AC", name="Active")

        preschool_type, created = InstitutionType.objects.get_or_create(char_id="pre",name="Preschool")
        primary_type, created = InstitutionType.objects.get_or_create(char_id="primary", name="Primary School")

        boundary_india, created = Boundary.objects.get_or_create(id=1,name="India", boundary_type=country, dise_slug="India",status=active_status)
        boundary_karnataka, created = Boundary.objects.get_or_create(id=2,parent=boundary_india,name="Karnataka", boundary_type=state, dise_slug="Karnataka",status=active_status)
        Boundary.objects.get_or_create(id=3, parent=boundary_karnataka, name="Test District",boundary_type=school_district, type=preschool_type, dise_slug="Test District", status=active_status)
    

    def test_list(self):

       #credentials = base64.b64encode(bytes('admin:admin','utf8')).decode('utf8')
       # self.client.defaults['HTTP_AUTHORIZATION'] = 'NONE'
        self.client.force_authenticate(user=self.user)
        url = '/api/v1/ka/boundary/admin1s'
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        data = json.loads(response.content)
        self.assertIsNotNone(data)
