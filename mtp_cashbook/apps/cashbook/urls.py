from django.conf.urls import url

from .views import CreditBatchListView, CreditsLockedView, \
    CreditHistoryView, DashboardView

urlpatterns = [
    url(r'^$', DashboardView.as_view(), name='dashboard'),
    url(r'^dashboard-batch-complete/$', DashboardView.as_view(),
        name='dashboard-batch-complete'),
    url(r'^dashboard-batch-incomplete/$', DashboardView.as_view(),
        name='dashboard-batch-incomplete'),
    url(r'^dashboard-batch-discard/$', DashboardView.as_view(discard_batch=True),
        name='dashboard-batch-discard'),
    url(r'^dashboard-unlocked-payments/$', DashboardView.as_view(),
        name='dashboard-unlocked-payments'),

    url(r'^locked/$', CreditsLockedView.as_view(), name='credits-locked'),

    url(r'^batch/$', CreditBatchListView.as_view(), name='credit-list'),

    url(r'^history/$', CreditHistoryView.as_view(), name='credit-history'),
]
