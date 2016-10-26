from celery import shared_task

from .models import Order


@shared_task
def check_order(order_id):
    # TODO: add function comments

    # TODO: Prefetch
    order = Order.objects.get(id=order_id)

    if not order.complete:  # Delete the order and release stock if timed out
        for order_product in order.orderproduct_set.all():
            order_product.product.release_stock(order_product.quantity)

        order.delete()
