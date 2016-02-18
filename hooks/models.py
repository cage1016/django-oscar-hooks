from oscar.core.loading import is_model_registered

from hooks import abstract_models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

if not is_model_registered('hooks', 'Hook'):
    class Hook(abstract_models.AbstractHook):
        pass

if not is_model_registered('hooks', 'HookEvent'):
    class HookEvent(abstract_models.AbstractHookEvent):
        pass

if not is_model_registered('hooks', 'HookLog'):
    class HookLog(abstract_models.AbstractHookLog):
        pass

if not is_model_registered('hooks', 'HookSignalType'):
    class HookSignalType(abstract_models.AbstractSignalType):
        pass


@receiver(post_save, sender=HookEvent, dispatch_uid="update_hookevent_count")
@receiver(post_delete, sender=HookEvent, dispatch_uid="delete_hookevent_count")
def update_hookevent_count(sender, instance, **kwargs):
    count = HookEvent.objects.all().filter(hook=instance.hook.pk).count()
    instance.hook.event_count = count
    instance.hook.save()
