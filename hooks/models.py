from oscar.core.loading import is_model_registered

from hooks import abstract_models

if not is_model_registered('hooks', 'HookClass'):
  class HookClass(abstract_models.AbstractHookClass):
    pass

if not is_model_registered('hooks', 'Hook'):
  class Hook(abstract_models.AbstractHook):
    pass

if not is_model_registered('hooks', 'HookEvent'):
  class HookEvent(abstract_models.AbstractHookEvent):
    pass

if not is_model_registered('hooks', 'HookLog'):
  class HookLog(abstract_models.AbstractHookLog):
    pass
