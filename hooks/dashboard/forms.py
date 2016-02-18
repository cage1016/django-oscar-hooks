from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_model, get_class

SignalTypeSelect = get_class('hooks.dashboard.widgets', 'SignalTypeSelect')

ProductClass = get_model('catalogue', 'ProductClass')

Hook = get_model('hooks', 'Hook')
HookEvent = get_model('hooks', 'HookEvent')


class ProductClassSelectForm(forms.Form):
    """
    Form which is used before creating a product to select it's product class
    """

    product_class = forms.ModelChoiceField(
            label=_("Choose a new Hook of Type"),
            empty_label=_("-- Choose product type --"),
            queryset=ProductClass.objects.all())

    def __init__(self, *args, **kwargs):
        """
        If there's only one product class, pre-select it
        """
        super(ProductClassSelectForm, self).__init__(*args, **kwargs)
        qs = self.fields['product_class'].queryset
        if not kwargs.get('initial') and len(qs) == 1:
            self.fields['product_class'].initial = qs[0]


class HookForm(forms.ModelForm):
    class Meta:
        model = Hook
        fields = ['name', 'error_report_email', 'description']

    def __init__(self, product_class, user, *args, **kwargs):
        super(HookForm, self).__init__(*args, **kwargs)
        self.instance.product_class = product_class


class HookEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HookEventForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.fields['signal_type'].widget.attrs['class'] = "select2"

    class Meta:
        model = HookEvent
        fields = ['hook', 'URL', 'signal_type', 'extra_headers']
        widgets = {
            'signal_type': SignalTypeSelect,
        }


BaseHookEventFormSet = inlineformset_factory(Hook, HookEvent, form=HookEventForm, extra=2, fk_name='hook')


class HookEventFormSet(BaseHookEventFormSet):
    def __init__(self, product_class, user, *args, **kwargs):
        super(HookEventFormSet, self).__init__(*args, **kwargs)
