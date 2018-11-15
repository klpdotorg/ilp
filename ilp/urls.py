
from django.utils.translation import gettext_lazy as _
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework_swagger.views import get_swagger_view
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from common.views import StaticPageView, BlogFeedView
from schools.views import (
    AdvancedMapView, BoundaryPageView,
    NewBoundaryPageView, SchoolPageView
)
from users.views import (
    EmailVerificationView,
    ProfilePageView,
    ProfileEditPageView
)
from assessments.views import SYSView, gka_dashboard, gp_contest_dashboard
from reports.views import view_report, download_report, SendReport, ReportAnalytics, download_analytics


api_docs_view = get_swagger_view(title='ILP API')


urlpatterns = [
    url(r'^back-office/', admin.site.urls),

    # Home page
    url(r'^$', StaticPageView.as_view(
        template_name='home.html',
    ), name='home'),
    url(r'^status/$', StaticPageView.as_view(
        template_name='comingsoon.html'
    ), name='status'),
    # Users/Auth related pages

    url(r'^users/verify_email',
        EmailVerificationView.as_view(), name='user_email_verify'),

    url(r'^profile/(?P<pk>[0-9]+)/$',
        ProfilePageView.as_view(), name='profile_page'),

    url(r'^profile/(?P<pk>[0-9]+)/edit$',
        ProfileEditPageView.as_view(), name='profile_edit_page'),

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

    url(r'^partners/akshara/maths/$', StaticPageView.as_view(
        template_name='partners/akshara/maths.html',
    ), name='maths_programme'),
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

    # story dashboard
    url(r'^stories/$', StaticPageView.as_view(
        template_name='story_dashboard.html'
    ), name='story_dashboard'),

    # Share you story
    url(r'^sys/(?P<value>\d+)/$', StaticPageView.as_view(
        template_name='sys_form.html'
    ), name='sys_form'),

    # Reports page
    url(r'^reports/$', StaticPageView.as_view(
        template_name='reports.html',
    ), name='reports'),

    # The GKA dashboard
    url(r'^gka/$', gka_dashboard, name='gka_dashboard'),

    # GP Contest Dashboard
    url(r'^gp-contest/$', gp_contest_dashboard, name='gp_contest_dashboard'),

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

    # share your story form
    url(r'^sys/(?P<pk>[0-9]+)$', SYSView.as_view(), name='sys'),

    # API URLs.
    url(r'^api/v1/', include('ilp.api_urls')),
    url(r'^api/docs/', api_docs_view, name='api_docs'),

    #URLs for viewing generated reports
    url(r'^reportgen/sendreport/$', SendReport.as_view(), name='send_report'),
    # url(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/$', view_report, name='view_report_no_track_id'),
    # url(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/(?P<tracking_id>([a-z]|[0-9])*)/$', view_report, name='view_report'),
    # url(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/download', download_report, name='download_report_no_track_id'),
    # url(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/(?P<tracking_id>([a-z]|[0-9])*)/download', download_report, name='download_report'),
    url(r'^reportanalytics/$', ReportAnalytics.as_view(), name='report_analytics'),
    url(r'^reportanalytics/download$', download_analytics, name='download_analytics'),

    # report pages
    url(r'^reports/search$', StaticPageView.as_view(
        template_name='report_search.html'
        ), name='report_search'),

    url(r'^reports/demographics/(?P<report_type>electedrep|boundary)/(?P<language>english|kannada)/(?P<id>[0-9]+)/$', StaticPageView.as_view(
        template_name='demographics.html'
        ), name='demographics'),

    url(r'^reports/demographics_dise/(?P<report_type>electedrep|boundary)/(?P<language>english|kannada)/(?P<id>[0-9]+)/$', StaticPageView.as_view(
        template_name='demographics_dise.html'
        ), name='demographics_dise'),

    url(r'^reports/finance/(?P<report_type>electedrep|boundary)/(?P<language>english|kannada)/(?P<id>[0-9]+)/$', StaticPageView.as_view(
        template_name='finance.html'
        ), name='finance'),

    url(r'^reports/infrastructure/(?P<report_type>electedrep|boundary)/(?P<language>english|kannada)/(?P<id>[0-9]+)/$', StaticPageView.as_view(
        template_name='infrastructure.html'
        ), name='infrastructure'),

    url(r'^reports/surveys$', StaticPageView.as_view(
        template_name='story_report.html'
        ), name='stories'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += i18n_patterns(
    url(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/$', view_report, name='view_report_no_track_id'),
    url(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/(?P<tracking_id>([a-z]|[0-9])*)/$', view_report, name='view_report'),
    url(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/download', download_report, name='download_report_no_track_id'),
    url(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/(?P<tracking_id>([a-z]|[0-9])*)/download', download_report, name='download_report'),
)

