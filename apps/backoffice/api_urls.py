from django.urls import re_path
# from django.views.decorators.cache import cache_page


from backoffice.api_views import ( DataAnalysis)

urlpatterns = [
    # Reports urls
    re_path(r'analysis/*/$',
        DataAnalysis.as_view(), name='analyse')
]
 
