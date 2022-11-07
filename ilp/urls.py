
from django.utils.translation import gettext_lazy as _
from django.urls import re_path, include
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
    # Home page
    re_path(r'^$', StaticPageView.as_view(
        template_name='home.html',
    ), name='home'),
    re_path(r'^status/$', StaticPageView.as_view(
        template_name='comingsoon.html'
    ), name='status'),
    # Users/Auth related pages

    re_path(r'^users/verify_email',
        EmailVerificationView.as_view(), name='user_email_verify'),

    re_path(r'^profile/(?P<pk>[0-9]+)/$',
        ProfilePageView.as_view(), name='profile_page'),

    re_path(r'^profile/(?P<pk>[0-9]+)/edit$',
        ProfileEditPageView.as_view(), name='profile_edit_page'),

    # Map
    re_path(r'^map/$', StaticPageView.as_view(
        template_name='map.html',
        extra_context={
            'hide_footer': True,
        }),
        name='map'),

    re_path(r'^advanced-map/$', AdvancedMapView.as_view(), name='advanced_map'),

    # Data page
    re_path(r'^data/$', StaticPageView.as_view(
        template_name='data.html',
    ), name='data'),
    re_path(r'text/data$', RedirectView.as_view(url='/data')),
    re_path(r'listFiles/2$', RedirectView.as_view(url='/data')),

    # Partner pages
    re_path(r'^partners/akshara/reading/$', StaticPageView.as_view(
        template_name='partners/akshara/reading.html',
    ), name='reading_programme'),

    re_path(r'^partners/sikshana/reading/$', StaticPageView.as_view(
        template_name='partners/sikshana/reading.html',
    ), name='sikshana_programme'),

    re_path(r'^partners/akshara/maths/$', StaticPageView.as_view(
        template_name='partners/akshara/maths.html',
    ), name='maths_programme'),

    re_path(r'^partners/pratham/learn-out-of-the-box/$', StaticPageView.as_view(
        template_name='partners/pratham/learn.html',
    ), name='partners_pratham_learn'),

    re_path(r'^partners/akshara/preschool/$', StaticPageView.as_view(
        template_name='partners/akshara/preschool.html',
    ), name='preschool_programme'),

    re_path(r'^partners/akshara/library/$', StaticPageView.as_view(
        template_name='partners/akshara/library.html',
    ), name='library_programme'),

    re_path(r'^volunteer/$', StaticPageView.as_view(
        template_name='volunteer.html',
    ), name='volunteer'),
    re_path(r'text/volunteer/$', RedirectView.as_view(url='/volunteer/')),

    # Programme -> partners redirect pages
    # Akshara reading programme
    re_path(r'^programmes/reading/$',
        RedirectView.as_view(url='/partners/akshara/reading/')),

    re_path(r'text/reading/$',
        RedirectView.as_view(url='/partners/akshara/reading/')),

    # Akshara Math programme
    re_path(r'^text/maths/$',
        RedirectView.as_view(url='/partners/akshara/maths/')),

    re_path(r'^partners/akshara/maths/$', StaticPageView.as_view(
        template_name='partners/akshara/maths.html',
    ), name='maths_programme'),
    # Akshara preschool
    re_path(r'^text/preschool/$',
        RedirectView.as_view(url='/partners/akshara/preschool/')),

    # Akshara library
    re_path(r'^text/library/$',
        RedirectView.as_view(url='/partners/akshara/library/')),

    # Sikshana reading
    re_path(r'^programmes/sikshana/$',
        RedirectView.as_view(url='/partners/sikshana/reading/')),

    re_path(r'^text/sikshana/$',
        RedirectView.as_view(url='/partners/sikshana/reading/')),

    # story dashboard
    re_path(r'^stories/$', StaticPageView.as_view(
        template_name='story_dashboard.html'
    ), name='story_dashboard'),

    # Share you story
    re_path(r'^sys/(?P<value>\d+)/$', StaticPageView.as_view(
        template_name='sys_form.html'
    ), name='sys_form'),

    # Reports page
    re_path(r'^reports/$', StaticPageView.as_view(
        template_name='reports.html',
    ), name='reports'),

    # The GKA dashboard
    re_path(r'^gka/$', gka_dashboard, name='gka_dashboard'),

    # GP Contest Dashboard
    re_path(r'^gp-contest/$', gp_contest_dashboard, name='gp_contest_dashboard'),

    re_path(r'text/reports/$', RedirectView.as_view(url='/reports')),

    # About pages
    re_path(r'^about/$', StaticPageView.as_view(
        template_name='aboutus.html',
    ), name='aboutus'),

    re_path(r'text/aboutus/$', RedirectView.as_view(url='/about')),

    re_path(r'^partners/$', StaticPageView.as_view(
        template_name='partners.html',
    ), name='partners'),

    re_path(r'text/partners/$', RedirectView.as_view(url='/partners')),

    re_path(r'^disclaimer/$', StaticPageView.as_view(
        template_name='disclaimer.html',
    ), name='disclaimer'),

    re_path(r'text/disclaimer/$', RedirectView.as_view(url='/disclaimer')),

    re_path(r'blog-feed/$', BlogFeedView.as_view(), name='blog_feed'),

    # boundary page
    re_path(r'^boundary/(?P<pk>[0-9]+)/$', BoundaryPageView.as_view(), name='boundary_page'),

    re_path(r'^(?P<boundary_type>preschool-district|primary-district|circle|cluster|project|block)/(?P<pk>[0-9]+)/$', NewBoundaryPageView.as_view(), name='boundary_page_new'),

    re_path(r'^school/(?P<pk>[0-9]+)/$',
                    SchoolPageView.as_view(), name='school_page'),

    # share your story form
    re_path(r'^sys/(?P<pk>[0-9]+)$', SYSView.as_view(), name='sys'),

    # API URLs.
    re_path(r'^api/v1/', include('ilp.api_urls')),
    re_path(r'^api/docs/', api_docs_view, name='api_docs'),

    # Backoffice URLs.
    re_path(r'^backoffice/', include('backoffice.urls')),

    # URLs for viewing generated reports
    re_path(r'^reportgen/sendreport/$', SendReport.as_view(), name='send_report'),
    # re_path(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/$', view_report, name='view_report_no_track_id'),
    # re_path(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/(?P<tracking_id>([a-z]|[0-9])*)/$', view_report, name='view_report'),
    # re_path(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/download', download_report, name='download_report_no_track_id'),
    # re_path(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/(?P<tracking_id>([a-z]|[0-9])*)/download', download_report, name='download_report'),
    re_path(r'^reportanalytics/', ReportAnalytics.as_view(), name='report_analytics'),
    re_path(r'^downloadanalytics/', download_analytics, name='download_analytics'),

    # report pages
    re_path(r'^reports/search$', StaticPageView.as_view(
        template_name='report_search.html'
        ), name='report_search'),

    re_path(r'^reports/demographics/(?P<report_type>electedrep|boundary)/(?P<language>english|kannada)/(?P<id>[0-9]+)/$', StaticPageView.as_view(
        template_name='demographics.html'
        ), name='demographics'),

    re_path(r'^reports/demographics_dise/(?P<report_type>electedrep|boundary)/(?P<language>english|kannada)/(?P<id>[0-9]+)/$', StaticPageView.as_view(
        template_name='demographics_dise.html'
        ), name='demographics_dise'),

    re_path(r'^reports/finance/(?P<report_type>electedrep|boundary)/(?P<language>english|kannada)/(?P<id>[0-9]+)/$', StaticPageView.as_view(
        template_name='finance.html'
        ), name='finance'),

    re_path(r'^reports/infrastructure/(?P<report_type>electedrep|boundary)/(?P<language>english|kannada)/(?P<id>[0-9]+)/$', StaticPageView.as_view(
        template_name='infrastructure.html'
        ), name='infrastructure'),

    re_path(r'^reports/surveys$', StaticPageView.as_view(
        template_name='story_report.html'
        ), name='stories'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += i18n_patterns(
    re_path(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/$', view_report, name='view_report_no_track_id'),
    re_path(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/(?P<tracking_id>([a-z]|[0-9])*)/$', view_report, name='view_report'),
    re_path(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/download', download_report, name='download_report_no_track_id'),
    re_path(r'^reportgen/(?P<report_id>([a-z]|[0-9])+)/(?P<tracking_id>([a-z]|[0-9])*)/download', download_report, name='download_report'),
)

