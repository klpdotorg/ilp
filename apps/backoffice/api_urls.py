from django.conf.urls import url
# from django.views.decorators.cache import cache_page


from backoffice.api_views import ( DataAnalysis)

urlpatterns = [
    # Reports urls
    url(r'analysis/*/$',
        DataAnalysis.as_view(), name='analyse')
]
 
