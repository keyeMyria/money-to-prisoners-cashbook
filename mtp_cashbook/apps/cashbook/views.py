from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from mtp_cashbook.apps.mtp_auth.api_client import get_connection


class TransactionBatchListView(ListView):

    template_name = 'cashbook/transaction_batch_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.client = get_connection(request)
        return super(TransactionBatchListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # these are hardcoded for now,
        # until there is a /user/me/ endpoint
        PRISON = 'IXB'
        USER_ID = 1

        resp = self.client.transactions(PRISON)(USER_ID).get(status='pending')
        if resp.get('count') == 0:
            resp = self.client.transactions(PRISON)(USER_ID).take.post()
        return resp.get('results', [])
