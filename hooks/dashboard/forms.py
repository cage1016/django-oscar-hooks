from django import forms
from django.core import exceptions
from django.forms.models import inlineformset_factory, modelformset_factory
from django.utils.translation import ugettext_lazy as _
from treebeard.forms import movenodeform_factory

from oscar.core.loading import get_class, get_model
from oscar.core.utils import slugify
from oscar.forms.widgets import ImageInput

Product = get_model('catalogue', 'Product')

HookClass = get_model('hooks', 'HookClass')
Hook = get_model('hooks', 'Hook')
HookEvent = get_model('hooks', 'HookEvent')


class HookForm(forms.ModelForm):
  class Meta:
    model = Hook
    fields = ['name', 'description', 'product']

  def __init__(self, hook_class, user, *args, **kwargs):
    super(HookForm, self).__init__(*args, **kwargs)
    self.instance.hook_class = hook_class

    if 'name' in self.fields:
      self.fields['name'].widget = forms.TextInput(
          attrs={'autocomplete': 'off'})

    if 'product' in self.fields:
      if not user.is_staff:
        self.fields['product'].queryset = Product.objects.filter(stockrecords__partner__users__pk=user.pk)


class HookClassForm(forms.ModelForm):
  class Meta:
    model = HookClass
    fields = ['name', 'email']


class HookClassSelectForm(forms.Form):
  """
  Form which is used before creating a hook to select it's hook class
  """

  hook_class = forms.ModelChoiceField(
      label=_("Create a new hook of type"),
      empty_label=_("-- Choose hook type --"),
      queryset=HookClass.objects.all())

  def __init__(self, *args, **kwargs):
    """
    If there's only one product class, pre-select it
    """
    super(HookClassSelectForm, self).__init__(*args, **kwargs)
    qs = self.fields['hook_class'].queryset
    if not kwargs.get('initial') and len(qs) == 1:
      self.fields['hook_class'].initial = qs[0]


class HookEventForm(forms.ModelForm):
  class Meta:
    model = HookEvent
    fields = ['hook', 'signal_type', 'URL', 'extra_headers']

  def __init__(self, *args, **kwargs):
    super(HookEventForm, self).__init__(*args, **kwargs)

    if 'URL' in self.fields:
      self.fields['URL'].widget = forms.URLInput(attrs={
        'placeholder': 'Hook URL',
      })

    if 'extra_header_data' in self.fields:
      self.fields['extra_header_data'].widget = forms.Textarea(attrs={
        'placeholder': 'extara JSON data'
      })


BaseHookEventFormSet = inlineformset_factory(Hook, HookEvent, form=HookEventForm, extra=0, min_num=0,
                                             fields=('signal_type', 'URL', 'extra_headers',))


class HookEventFormSet(BaseHookEventFormSet):
  def __init__(self, hook_class, user, *args, **kwargs):
    super(HookEventFormSet, self).__init__(*args, **kwargs)
