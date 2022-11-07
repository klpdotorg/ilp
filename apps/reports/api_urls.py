from django.urls import re_path
# from django.views.decorators.cache import cache_page


from reports.api_views import (
    DemographicsBoundaryReportDetails, BoundarySummaryReport,
    DemographicsBoundaryComparisonDetails, DiseBoundaryDetails,
    DemographicsElectedRepReportDetails, DemographicsElectedRepComparisonDetails,
    ElectedRepInfo, ElectedRepSummaryReport
)

urlpatterns = [
    # Reports urls
    re_path(r'summary/boundary/$',
        BoundarySummaryReport.as_view(), name='api_reports_detail'),
    re_path(r'demographics/boundary/details/$',
        DemographicsBoundaryReportDetails.as_view(), name='api_reports_detail'),
    re_path(r'summary/electedrep/$',
        ElectedRepSummaryReport.as_view(), name='api_reports_detail'),
    re_path(r'demographics/electedrep/details/$',
        DemographicsElectedRepReportDetails.as_view(), name='api_reports_detail'),
    re_path(r'demographics/boundary/comparison/$',
        DemographicsBoundaryComparisonDetails.as_view(), name='api_reports_detail'),
    re_path(r'demographics/electedrep/comparison/$',
        DemographicsElectedRepComparisonDetails.as_view(),
        name='api_reports_detail'),
    re_path(r'dise/boundary/$',
        DiseBoundaryDetails.as_view(), name='api_reports_detail'),
    re_path(r'electedrep/$', ElectedRepInfo.as_view(), name='api_reports_detail')
]
