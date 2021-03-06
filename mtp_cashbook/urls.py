from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control
from django.views.generic.base import RedirectView, TemplateView
from django.views.i18n import JavaScriptCatalog
from moj_irat.views import HealthcheckView, PingJsonView
from mtp_common.auth import api_client


class LandingView(TemplateView):
    template_name = 'landing.html'

    def get_context_data(self, **kwargs):
        if self.request.user.has_perm('auth.change_user'):
            response = api_client.get_api_session(self.request).get('requests/', params={'page_size': 1})
            kwargs['user_request_count'] = response.json().get('count')
        return super().get_context_data(
            start_page_url=settings.START_PAGE_URL,
            **kwargs
        )


urlpatterns = i18n_patterns(
    url(r'^$', login_required(LandingView.as_view()), name='home'),

    url(r'^', include('cashbook.urls')),
    url(r'^disbursements/', include('disbursements.urls', namespace='disbursements')),

    url(r'^', include('mtp_auth.urls')),
    url(r'^', include('mtp_common.user_admin.urls')),

    url(r'^', include('feedback.urls')),

    url(r'^js-i18n.js$', cache_control(public=True, max_age=86400)(JavaScriptCatalog.as_view()), name='js-i18n'),

    url(r'^404.html$', lambda request: TemplateResponse(request, 'mtp_common/errors/404.html', status=404)),
    url(r'^500.html$', lambda request: TemplateResponse(request, 'mtp_common/errors/500.html', status=500)),
)

urlpatterns += [
    url(r'^ping.json$', PingJsonView.as_view(
        build_date_key='APP_BUILD_DATE',
        commit_id_key='APP_GIT_COMMIT',
        version_number_key='APP_BUILD_TAG',
    ), name='ping_json'),
    url(r'^healthcheck.json$', HealthcheckView.as_view(), name='healthcheck_json'),

    url(r'^favicon.ico$', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.ico', permanent=True)),
    url(r'^robots.txt$', lambda request: HttpResponse('User-agent: *\nDisallow: /', content_type='text/plain')),
]

handler404 = 'mtp_common.views.page_not_found'
handler500 = 'mtp_common.views.server_error'
handler400 = 'mtp_common.views.bad_request'
