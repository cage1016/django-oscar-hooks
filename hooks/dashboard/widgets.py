from django.core.urlresolvers import reverse_lazy

from oscar.forms.widgets import RemoteSelect, MultipleRemoteSelect


class SignalTypeSelect(RemoteSelect):
    # Implemented as separate class instead of just calling
    # AjaxSelect(data_url=...) for overridability and backwards compatibility
    lookup_url = reverse_lazy('signal-type-lookup')
