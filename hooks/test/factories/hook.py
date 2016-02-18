# coding: utf-8

import factory
from jsonfield import JSONField

from oscar.core.loading import get_model

__all__ = [
    'HookFactory',
    'HookEventFactory'
]

class SignalTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_model('hooks','HookSignalType')

    name = u"order_place"


class HookFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_model('hooks', 'Hook')

    name = u"Apps Hook"
    user = factory.SubFactory('oscar.test.factories.customer.UserFactory')
    description = "this is Apps Hook"


class HookEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_model('hooks', 'HookEvent')

    hook = factory.SubFactory(HookFactory)
    signal_type = factory.SubFactory(SignalTypeFactory)
    URL = "http://localhost:2000/product_viewed"
    extra_headers = {"token": "this-is-token"}
