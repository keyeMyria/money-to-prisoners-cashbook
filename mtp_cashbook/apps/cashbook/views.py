from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, TemplateView

from moj_auth import api_client

from .forms import ProcessTransactionBatchForm, DiscardLockedTransactionsForm


class DashboardView(TemplateView):
    template_name = 'cashbook/dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.client = api_client.get_connection(request)
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(DashboardView, self).get_context_data(**kwargs)

        # new transactions == available + my locked
        transaction_client = self.client.cashbook.transactions
        available = transaction_client.get(status='available')
        my_locked = transaction_client.get(user=self.request.user.pk, status='locked')
        locked = transaction_client.get(status='locked')
        context_data['new_transactions'] = available['count'] + my_locked['count']
        context_data['locked_transactions'] = locked['count']
        return context_data


class TransactionBatchListView(FormView):

    form_class = ProcessTransactionBatchForm
    template_name = 'cashbook/transaction_batch_list.html'
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        form_kwargs = super(TransactionBatchListView, self).get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TransactionBatchListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TransactionBatchListView, self).get_context_data(**kwargs)

        transaction_choices = context['form'].transaction_choices
        context['object_list'] = transaction_choices
        context['total'] = sum([x[1]['amount'] for x in transaction_choices])
        return context

    def form_valid(self, form):
        credited, discarded = form.save()

        if credited:
            messages.success(
                self.request,
                _(
                    'You\'ve credited %(credited)s payment%(plural)s to NOMIS.'
                ) % {
                    'credited': len(credited),
                    'plural': '' if len(credited) == 1 else 's'
                }
            )
        return super(TransactionBatchListView, self).form_valid(form)


class TransactionsLockedView(FormView):

    form_class = DiscardLockedTransactionsForm
    template_name = 'cashbook/transactions_locked.html'
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        form_kwargs = super(TransactionsLockedView, self).get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TransactionsLockedView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TransactionsLockedView, self).get_context_data(**kwargs)

        context['object_list'] = context['form'].transaction_choices
        return context

    def form_valid(self, form):
        discarded = form.save()

        messages.success(
            self.request,
            _(
                '%(discarded)s transaction%(plural)s unlocked successfully.'
            ) % {
                'discarded': len(discarded),
                'plural': '' if len(discarded) == 1 else 's'
            }
        )
        return super(TransactionsLockedView, self).form_valid(form)
