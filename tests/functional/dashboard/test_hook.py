from django.core.urlresolvers import reverse

from oscar.core.loading import get_model
from oscar.test.testcases import WebTestCase, add_permissions

from oscar.test.factories import (
    CategoryFactory, PartnerFactory, ProductFactory, ProductAttributeFactory)

from hooks.test.factories import (
    HookEventFactory, HookFactory
)

ProductClass = get_model('catalogue', 'ProductClass')
Hook = get_model('hooks', 'Hook')


class TestAStaffUser(WebTestCase):
    is_staff = True

    def setUp(self):
        super(TestAStaffUser, self).setUp()
        self.partner = PartnerFactory()

    def test_can_create_hook_with_hook_event(self):
        hookevent = HookEventFactory()
        hook = HookFactory()
        product_class = ProductClass.objects.create(name="Book")

        page = self.get(reverse('hook-create', kwargs={"hook_class_slug": product_class.slug}))

        form = page.form
        form["name"] = u'books'
        form["description"] = u'this is description'
        form["hookevent_set-0-id"] = hook
        form["hookevent_set-0-signal_type"] = hookevent.signal_type
        form["hookevent_set-0-URL"] = hookevent.URL
        form["hookevent_set-0-extra_headers"] = hookevent.extra_headers
        response = form.submit(name='action', value='save')

        assert Hook.objects.count() == 2
