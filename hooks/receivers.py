"""
receivers

django-oscar hooks handle
"""

from django.forms.models import model_to_dict
from django.dispatch import receiver

from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model

from hooks.tasks import run_hook_tasks_job

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
Hook = get_model('hooks', 'Hook')

Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
User = get_user_model()


def filer_hookevent(product, singal_type):
    # what kind of product class product belong to
    target_product_class = product.product_class

    partner = StockRecord.objects.all()
    partner = partner.filter(product=product)
    owner = User.objects.filter(partners__in=[f.partner for f in partner])

    qs = HookEvent.objects.all()
    qs = qs.filter(signal_type=singal_type)
    qs = qs.filter(hook__user=owner)
    qs = qs.filter(hook__product_class=target_product_class)

    return qs


@receiver(product_viewed)
def receive_product_viewed(sender, product, user, request, response, **kwargs):
    """

    :param sender:
    :param product:
    :param user:
    :param request:
    :param response:
    :param kwargs:
    :return:
    """

    qs = filer_hookevent(product, 1)
    if qs:
        data = {
            "user": dict(user=user.username, email=user.email),
            "product": model_to_dict(product)
        }
        run_hook_tasks_job(qs, data)


@receiver(user_search)
def receive_user_search(sender, query, user, **kwargs):
    pass


@receiver(user_registered)
def receive_user_registered(sender, request, user, **kwargs):
    pass


@receiver(basket_addition)
def receive_basket_addition(sender, request, product, user, **kwargs):
    """
    Raised when a product is added to a basket.

    :param sender:
    :param request:
    :param product:
    :param user:
    :param kwargs:
    :return:
    """

    qs = filer_hookevent(product, 4)
    if qs:
        data = {
            "user": dict(user=user.username, email=user.email),
            "product": model_to_dict(product)
        }
        run_hook_tasks_job(qs, data)


@receiver(voucher_addition)
def receive_voucher_addition(sender, basket, voucher, **kwargs):
    pass


@receiver(start_checkout)
def receive_start_checkout(sender, request, **kwargs):
    pass


@receiver(pre_payment)
def receive_pre_payment(sender, view, **kwargs):
    pass


@receiver(post_payment)
def receive_post_payment(sender, view, **kwargs):
    pass


@receiver(order_placed)
def receive_order_placed(sender, order, user, **kwargs):
    """

    :param sender:
    :param order:
    :param user:
    :param kwargs:
    :return:
    """

    for line in order.basket.lines.all():
        product = line.product
        qs = filer_hookevent(product, 9)

        if qs:
            data = {
                "user": dict(user=user.username, email=user.email),
                "order": order.number,
                "product": model_to_dict(product),
                "price_excl_tax": line.price_excl_tax,
                "price_incl_tax": line.price_incl_tax,
                "quantity": line.quantity
            }
            run_hook_tasks_job(qs, data)


@receiver(post_checkout)
def receive_post_checkout(sender, order, user, request, response, **kwargs):
    pass


@receiver(review_added)
def receive_review_created(sender, review, user, request, response, **kwargs):
    pass
