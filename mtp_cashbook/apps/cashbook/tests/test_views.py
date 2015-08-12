import mock

from django.core.urlresolvers import reverse

from core.testing.testcases import MTPBaseTestCase


class DashboardViewTestCase(MTPBaseTestCase):

    @mock.patch('cashbook.views.api_client')
    def __call__(self, result, mocked_api_client, *args, **kwargs):
        self.mocked_api_client = mocked_api_client
        super(DashboardViewTestCase, self).__call__(result, *args, **kwargs)

    @property
    def dashboard_url(self):
        return reverse('dashboard')

    def test_cannot_access_if_not_logged_in(self):
        response = self.client.get(self.dashboard_url)

        redirect_url = '{login_url}?next={dashboard_url}'.format(
            login_url=self.login_url,
            dashboard_url=self.dashboard_url
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_0_available_0_pending_gives_correct_new_count(self):
        self.login()

        conn = self.mocked_api_client.get_connection().transactions()
        conn.get.return_value = {'count': 0}  # available
        conn().get.return_value = {'count': 0}  # pending

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['new_transactions'], 0)

    def test_some_available_0_pending_gives_correct_new_count(self):
        self.login()

        conn = self.mocked_api_client.get_connection().transactions()
        conn.get.return_value = {'count': 21}  # available
        conn().get.return_value = {'count': 0}  # pending

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['new_transactions'], 21)

    def test_0_available_some_pending_gives_correct_new_count(self):
        self.login()

        conn = self.mocked_api_client.get_connection().transactions()
        conn.get.return_value = {'count': 0}  # available
        conn().get.return_value = {'count': 3}  # pending

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['new_transactions'], 3)

    def some_available_some_pending_gives_correct_new_count(self):
        self.login()

        conn = self.mocked_api_client.get_connection().transactions()
        conn.get.return_value = {'count': 21}  # available
        conn().get.return_value = {'count': 3}  # pending

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['new_transactions'], 24)