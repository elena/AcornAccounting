from django import forms
from django.forms.models import inlineformset_factory
from multiupload.fields import MultiFileField
from parsley.decorators import parsleyfy

from core.core import today_in_american_format, remove_trailing_zeroes

from entries.forms import (_set_minimal_queryset_for_account,
                           BaseBankTransactionFormSet)

from .models import CreditCardEntry, CreditCardTransaction


@parsleyfy
class CreditCardEntryForm(forms.ModelForm):
    """A Form for CreditCardEntries along with multiple CreditCardReceipts."""
    receipts = MultiFileField(
        min_num=0, max_num=99, max_file_size=1024 * 1024 * 100, required=False)

    class Meta(object):
        model = CreditCardEntry
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control'}),
            'card': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'merchant': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.TextInput(
                attrs={'size': 10, 'maxlength': 10, 'class': 'form-control',
                       'id': 'entry_amount'}),
            'comments': forms.Textarea(
                attrs={'rows': 2, 'cols': 50, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Set the initial date to today & change the name label."""
        super(CreditCardEntryForm, self).__init__(*args, **kwargs)
        self.fields['date'].label = "Purchase Date"
        self.fields['name'].label = "Your Name"
        if hasattr(self, 'instance') and self.instance.pk:
            formatted_date = self.instance.date.strftime('%m/%d/%Y')
            self.initial['date'] = formatted_date
            amount = self.instance.amount
            self.initial['amount'] = remove_trailing_zeroes(amount)
        else:
            self.initial['date'] = today_in_american_format()


@parsleyfy
class CreditCardTransactionForm(forms.ModelForm):
    class Meta(object):
        model = CreditCardTransaction
        fields = ('account', 'detail', 'amount')
        widgets = {
            'account': forms.Select(
                attrs={'class': 'account account-autocomplete '
                                'form-control enter-mod'}),
            'detail': forms.TextInput(
                attrs={'class': 'form-control enter-mod'}),
            'amount': forms.TextInput(
                attrs={'size': 10, 'maxlength': 10,
                       'class': 'amount form-control enter-mod'}),
        }

    def __init__(self, *args, **kwargs):
        super(CreditCardTransactionForm, self).__init__(*args, **kwargs)
        _set_minimal_queryset_for_account(self, 'account')
        amount = self.instance.amount
        if amount is not None:
            self.initial['amount'] = remove_trailing_zeroes(amount)


CreditCardTransactionFormSet = inlineformset_factory(
    CreditCardEntry, CreditCardTransaction, form=CreditCardTransactionForm,
    formset=BaseBankTransactionFormSet, extra=5, can_delete=True)
