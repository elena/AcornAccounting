import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase

from core.tests import create_header, create_account, create_entry
from entries.models import Transaction

from .models import Event


class QuickEventSearchViewTests(TestCase):
    """Test the quick_event_search view"""
    def setUp(self):
        """An Event to search for is required."""
        self.event = Event.objects.create(name='test event', number='1',
                                          date=datetime.date.today(),
                                          city='mineral', state='VA')

    def test_quick_event_success(self):
        """
        A `GET` to the `quick_event_search` view with an `event_id` should
        redirect to the Event's Detail page.
        """
        response = self.client.get(reverse('events.views.quick_event_search'),
                                   data={'event': self.event.id})
        self.assertRedirects(response,
                             reverse('events.views.show_event_detail',
                                     args=[self.event.id]))

    def test_quick_event_fail_not_event(self):
        """
        A `GET` to the `quick_event_search` view with an `event_id` should
        return a 404 if the Event does not exist.
        """
        response = self.client.get(
            reverse('events.views.quick_event_search'), data={'event': 9001})
        self.assertEqual(response.status_code, 404)

    def test_quick_event_fail_no_event(self):
        """
        A `GET` to the `quick_event_search` view with no `event_id` should
        return a 404.
        """
        response = self.client.get(reverse('events.views.quick_event_search'))
        self.assertEqual(response.status_code, 404)


class EventDetailViewTests(TestCase):
    """
    Test Event detail view
    """
    def setUp(self):
        """
        Events are tied to Transactions which require an Account.
        """
        self.asset_header = create_header('asset', cat_type=1)
        self.bank_account = create_account(
            'bank', self.asset_header, 0, 1, True)
        self.event = Event.objects.create(
            name='test event', city='mineral', state='VA',
            date=datetime.date.today(), number=420)

    def test_show_event_detail_view_initial(self):
        """
        A `GET` to the `show_event_detail` view with a valid `event_id` will
        return the respective `Event`.
        """
        general = create_entry(datetime.date.today(), 'general entry')
        Transaction.objects.create(journal_entry=general, balance_delta=20,
                                   account=self.bank_account, event=self.event)
        Transaction.objects.create(journal_entry=general, balance_delta=20,
                                   account=self.bank_account, event=self.event)

        response = self.client.get(reverse('events.views.show_event_detail',
                                           kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/event_detail.html')
        self.assertEqual(response.context['event'], self.event)

    def test_show_event_detail_view_initial_no_transactions(self):
        """
        A `GET` to the `show_event_detail` view with a valid `event_id` will
        return the respective `Event`. If no Transactions exist for this Event,
        all counters should return appropriately.
        """
        response = self.client.get(reverse('events.views.show_event_detail',
                                           kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/event_detail.html')
        self.assertEqual(response.context['event'], self.event)
        self.assertEqual(response.context['debit_total'], 0)
        self.assertEqual(response.context['credit_total'], 0)
        self.assertEqual(response.context['net_change'], 0)

    def test_show_event_detail_view_initial_only_credits(self):
        """
        A `GET` to the `show_event_detail` view with a valid `event_id` will
        also return the correct counters for `net_change`, `debit_total` and
        `credit_total` when only credits are present.
        """
        general = create_entry(datetime.date.today(), 'general entry')
        Transaction.objects.create(journal_entry=general, balance_delta=20,
                                   account=self.bank_account, event=self.event)
        Transaction.objects.create(journal_entry=general, balance_delta=20,
                                   account=self.bank_account, event=self.event)

        response = self.client.get(reverse('events.views.show_event_detail',
                                           kwargs={'event_id': self.event.id}))
        self.assertEqual(response.context['debit_total'], 0)
        self.assertEqual(response.context['credit_total'], 40)
        self.assertEqual(response.context['net_change'], 40)

    def test_show_event_detail_view_initial_only_debits(self):
        """
        A `GET` to the `show_event_detail` view with a valid `event_id` will
        also return the correct counters for `net_change`,`debit_total` and
        `credit_total` when only debits are present.
        """
        general = create_entry(datetime.date.today(), 'general entry')
        Transaction.objects.create(journal_entry=general, balance_delta=-20,
                                   account=self.bank_account, event=self.event)
        Transaction.objects.create(journal_entry=general, balance_delta=-20,
                                   account=self.bank_account, event=self.event)

        response = self.client.get(reverse('events.views.show_event_detail',
                                           kwargs={'event_id': self.event.id}))
        self.assertEqual(response.context['debit_total'], -40)
        self.assertEqual(response.context['credit_total'], 0)
        self.assertEqual(response.context['net_change'], -40)

    def test_show_event_detail_view_initial_debit_and_credit(self):
        """
        A `GET` to the `show_event_detail` view with a valid `event_id` will
        also return the correct counters for `net_change`, `debit_total` and
        `credit_total` when credits and debits are present.
        """
        general = create_entry(datetime.date.today(), 'general entry')
        Transaction.objects.create(journal_entry=general, balance_delta=20,
                                   account=self.bank_account, event=self.event)
        Transaction.objects.create(journal_entry=general, balance_delta=-20,
                                   account=self.bank_account, event=self.event)

        response = self.client.get(reverse('events.views.show_event_detail',
                                           kwargs={'event_id': self.event.id}))
        self.assertEqual(response.context['debit_total'], -20)
        self.assertEqual(response.context['credit_total'], 20)
        self.assertEqual(response.context['net_change'], 0)

    def test_show_event_detail_view_fail(self):
        """
        A `GET` to the `show_event_detail` view with an invalid `event_id` will
        return a 404.
        """
        response = self.client.get(reverse('events.views.show_event_detail',
                                           kwargs={'event_id': 90000001}))
        self.assertEqual(response.status_code, 404)
