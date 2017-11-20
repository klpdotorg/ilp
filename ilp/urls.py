from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework_swagger.views import get_swagger_view
from common.views import StaticPageView, BlogFeedView
from schools.views import ( 
    AdvancedMapView, BoundaryPageView,
    NewBoundaryPageView, SchoolPageView)

api_docs_view = get_swagger_view(title='ILP API')


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Static views (pages)
    # home page
    url(r'^$', StaticPageView.as_view(
        template_name='home.html',
    ), name='home'),

    # Map
    url(r'^map/$', StaticPageView.as_view(
        template_name='map.html',
        extra_context={
            'hide_footer': True,
        }),
        name='map'),

    url(r'^advanced-map/$', AdvancedMapView.as_view(), name='advanced_map'),


    # Data page
    url(r'^data/$', StaticPageView.as_view(
        template_name='data.html',
    ), name='data'),
    url(r'text/data$', RedirectView.as_view(url='/data')),
    url(r'listFiles/2$', RedirectView.as_view(url='/data')),

    # Partner pages
    url(r'^partners/akshara/reading/$', StaticPageView.as_view(
        template_name='partners/akshara/reading.html',
    ), name='reading_programme'),

    url(r'^partners/sikshana/reading/$', StaticPageView.as_view(
        template_name='partners/sikshana/reading.html',
    ), name='sikshana_programme'),

    url(r'^partners/akshara/maths/$', StaticPageView.as_view(
        template_name='partners/akshara/maths.html',
    ), name='maths_programme'),

    url(r'^partners/pratham/learn-out-of-the-box/$', StaticPageView.as_view(
        template_name='partners/pratham/learn.html',
    ), name='partners_pratham_learn'),

    url(r'^partners/akshara/preschool/$', StaticPageView.as_view(
        template_name='partners/akshara/preschool.html',
    ), name='preschool_programme'),

    url(r'^partners/akshara/library/$', StaticPageView.as_view(
        template_name='partners/akshara/library.html',
    ), name='library_programme'),

    url(r'^volunteer/$', StaticPageView.as_view(
        template_name='volunteer.html',
    ), name='volunteer'),
    url(r'text/volunteer/$', RedirectView.as_view(url='/volunteer/')),

    # Programme -> partners redirect pages
    # Akshara reading programme
    url(r'^programmes/reading/$',
        RedirectView.as_view(url='/partners/akshara/reading/')),

    url(r'text/reading/$',
        RedirectView.as_view(url='/partners/akshara/reading/')),

    # Akshara Math programme
    url(r'^text/maths/$',
        RedirectView.as_view(url='/partners/akshara/maths/')),

    # Akshara preschool
    url(r'^text/preschool/$',
        RedirectView.as_view(url='/partners/akshara/preschool/')),

    # Akshara library
    url(r'^text/library/$',
        RedirectView.as_view(url='/partners/akshara/library/')),

    # Sikshana reading
    url(r'^programmes/sikshana/$',
        RedirectView.as_view(url='/partners/sikshana/reading/')),

    url(r'^text/sikshana/$',
        RedirectView.as_view(url='/partners/sikshana/reading/')),

    # Reports page
    url(r'^reports/$', StaticPageView.as_view(
        template_name='reports.html',
    ), name='reports'),

    # GKA Dashboard
    url(r'^gka/$', StaticPageView.as_view(
        template_name='gka_dashboard.html'), name='gka_dashboard'),

    url(r'text/reports/$', RedirectView.as_view(url='/reports')),

    # About pages
    url(r'^about/$', StaticPageView.as_view(
        template_name='aboutus.html',
    ), name='aboutus'),

    url(r'text/aboutus/$', RedirectView.as_view(url='/about')),

    url(r'^partners/$', StaticPageView.as_view(
        template_name='partners.html',
    ), name='partners'),

    url(r'text/partners/$', RedirectView.as_view(url='/partners')),

    url(r'^disclaimer/$', StaticPageView.as_view(
        template_name='disclaimer.html',
    ), name='disclaimer'),

    url(r'text/disclaimer/$', RedirectView.as_view(url='/disclaimer')),

    url(r'blog-feed/$', BlogFeedView.as_view(), name='blog_feed'),

    # boundary page
    url(r'^boundary/(?P<pk>[0-9]+)/$', BoundaryPageView.as_view(), name='boundary_page'),

    url(r'^(?P<boundary_type>preschool-district|primary-district|circle|cluster|project|block)/(?P<pk>[0-9]+)/$', NewBoundaryPageView.as_view(), name='boundary_page_new'),

    url(r'^school/(?P<pk>[0-9]+)/$',
                    SchoolPageView.as_view(), name='school_page'),

    # API URLs.
    url(r'^api/v1/', include('ilp.api_urls')),
    url(r'^api/docs/', api_docs_view, name='api_docs'),
]
