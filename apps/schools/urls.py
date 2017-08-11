from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from schools.api_view import (
    InstitutionBasicViewSet, InstitutionInfoViewSet
)


router = DefaultRouter()
router.register(r'schools/list', InstitutionBasicViewSet, base_name='basic')
router.register(r'schools/info', InstitutionInfoViewSet, base_name='info')

urlpatterns = router.urls