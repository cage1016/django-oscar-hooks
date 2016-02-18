import pytest

from hooks.models import Hook


@pytest.mark.django_db
def test_hook_slug_will_be_update_when_name_save():
    hook = Hook(name=u"my hook")
    hook.save()
    assert hook.slug == u"my-hook"

    hook.name = u'1 3 2'
    hook.save()
    assert hook.slug == u'1-3-2'
