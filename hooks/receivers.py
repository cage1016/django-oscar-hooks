import logging
from django.forms.models import model_to_dict

log = logging.getLogger('MYAPP')

from django.dispatch import receiver
from oscar.core.loading import get_class, get_model
from tasks import run_hook_tasks_job

product_viewed = get_class('catalogue.signals', 'product_viewed')
user_search = get_class('search.signals', 'user_search')
user_registered = get_class('customer.signals', 'user_registered')
basket_addition = get_class('basket.signals', 'basket_addition')
voucher_addition = get_class('basket.signals', 'voucher_addition')
start_checkout = get_class('checkout.signals', 'start_checkout')
pre_payment = get_class('checkout.signals', 'pre_payment')
post_payment = get_class('checkout.signals', 'post_payment')
order_placed = get_class('order.signals', 'order_placed')
post_checkout = get_class('checkout.signals', 'post_checkout')
review_added = get_class('catalogue.reviews.signals', 'review_added')

HookEvent = get_model('hooks', 'HookEvent')


@receiver(product_viewed)
def receive_product_viewed(sender, product, user, request, response, **kwargs):
  qs = HookEvent.objects.all()
  qs = qs.filter(signal_type=1)
  qs = qs.filter(hook__product=product)
  data = {"product": model_to_dict(product)}

  run_hook_tasks_job(qs, data)


@receiver(user_search)
def receive_user_search(sender, query, user, **kwargs):
  pass


@receiver(user_registered)
def receive_user_registered(sender, request, user, **kwargs):
  pass


@receiver(basket_addition)
def receive_basket_addition(sender, request, product, user, **kwargs):
  pass


@receiver(voucher_addition)
def receive_voucher_addition(sender, basket, voucher, **kwargs):
  pass


@receiver(start_checkout)
def receive_start_checkout(sender, request, **kwargs):
  pass


@receiver(pre_payment)
def receive_pre_payment(sender, view, **kwargs):
  pass
  # qs = HookEvent.objects.all()
  # qs = qs.filter(signal_type=1)
  # qs = qs.filter(hook__product=product)
  # data = {"product": model_to_dict(product)}
  #
  # run_hook_tasks_job(qs, data)


@receiver(post_payment)
def receive_post_payment(sender, view, **kwargs):
  pass


@receiver(order_placed)
def receive_order_placed(sender, order, user, **kwargs):
  qs = HookEvent.objects.all()
  qs = qs.filter(signal_type=9)
  qs = qs.filter(hook__product__in=[line.product for line in order.basket._lines])

  data = {"order": model_to_dict(order), 'user': model_to_dict(user)}
  run_hook_tasks_job(qs, data)


@receiver(post_checkout)
def receive_post_checkout(sender, order, user, request, response, **kwargs):
  log.info("--- post checkout ---")
  log.info(order)
  log.info(user)
  log.info("--- end post checkout ---")


@receiver(review_added)
def receive_review_created(sender, review, user, request, response, **kwargs):
  pass
