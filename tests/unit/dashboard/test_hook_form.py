from django.test import TestCase

from hooks.dashboard import forms
from hooks.test import factories
from oscar.test import factories as oscar_factories


class TestCreateHookForm(TestCase):
    def setUp(self):
        self.product_class = oscar_factories.ProductClassFactory()
        self.user = oscar_factories.UserFactory()

    def submit(self, data):
        return forms.HookForm(self.product_class, self.user, data=data)

    def test_validates_that_must_have_name_and_error_report_email(self):
        form = self.submit({"name": "Apps Hook", "error_report_email": "aa@bb.cc"})
        assert form.is_valid() == True


class TestCreateHookEventForm(TestCase):
    def setUp(self):
        pass

    def submit(self, data):
        return forms.HookEventForm(data=data)

    def test_validates_that_must_have_signal_type_and_url(self):
        form = self.submit({"URL": "http://localhost:2000/product_view"})
        assert form.is_valid() == False

        form = self.submit({"signal_type_id": 1, "URL": "http://localhost:2000/product_view",
                            "extra_headers": {}})
        assert form.is_valid() == True

        form = self.submit({"signal_type_id": 1, "URL": "http://localhost:2000/product_view",
                            'extra_headers': '{"time": datetime.datetime.now()}'})
        assert form.is_valid() == False

        form = self.submit({"signal_type_id": 1, "URL": "http://localhost:2000/product_view",
                            'extra_headers': {"data": 123}})
        assert form.is_valid() == True
