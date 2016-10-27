import json
from django.conf import settings
from django.shortcuts import get_object_or_404
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpBadRequest
from tastypie.resources import ModelResource
from tastypie.validation import Validation

from products.models import Product, Order, OrderProduct
from products.tasks import check_order


class ProductResource(ModelResource):

    class Meta(object):
        queryset = Product.objects.all()
        resource_name = 'product'
        allowed_methods = ['get', ]


class OrderProductResource(ModelResource):

    class Meta(object):
        queryset = OrderProduct.objects.all()
        resource_name = 'order_product'
        allowed_methods = ['get', ]


class OrderValidation(Validation):

    def is_valid(self, bundle, request=None):
        """
        Check the data received to make sure the product exists and that we
        have enough stock to make a sale. It takes into account the real stock
        of the product, that is, the stock minus the items reserved by other
        orders
        """
        errors = {}

        if not bundle.data.get('products'):
            errors['products'] = 'No products provided'
        else:
            for product_row in bundle.data.get('products'):
                product = get_object_or_404(
                    Product, pk=product_row.get('product')
                )
                if not product.enough_stock(int(product_row.get('quantity'))):
                    errors['quantity'] = 'Not enough stock'

        return errors


class OrderResource(ModelResource):

    # TODO: prefetch related
    products = fields.ToManyField(OrderProductResource, 'orderproduct_set',
                                  full=True)

    class Meta(object):
        queryset = Order.objects.all()
        resource_name = 'order'
        always_return_data = True
        validation = OrderValidation()
        authorization = Authorization()
        authentication = Authentication()
        allowed_methods = ['get', 'post', 'patch', ]

    def obj_update(self, bundle, **kwargs):
        """
        Marks an order as complete when the payment is done consolidating the
        stock (releasing the reserved units and setting them as sold)
        """
        body = json.loads(bundle.request.body.decode())

        if body.get('complete'):
            bundle.obj.complete = True
            bundle.obj.save()

            # Consolidate stock
            for order_product in bundle.obj.orderproduct_set.all():
                product = order_product.product
                quantity = order_product.quantity

                product.release_stock(quantity)
                product.stock -= quantity
                product.save()

    def save(self, bundle, skip_errors=False):
        """
        Creates a new pending order reserving the necessary stock and
        scheduling a task to release the stock in case the order is not paid
        within the ORDER_TIMEOUT
        """
        if not self.is_valid(bundle):
            raise ImmediateHttpResponse(HttpBadRequest())

        # It's already validated
        bundle.obj.save()

        for product_row in bundle.data.get('products'):
            product = Product.objects.get(id=product_row.get('product'))
            quantity = int(product_row.get('quantity'))

            OrderProduct(
                order=bundle.obj,
                product=product,
                quantity=quantity,
            ).save()

            # Reserve the stock to avoid other orders buying our stock while
            # we are paying
            product.reserve_stock(quantity)

        # Schedule the task to check the order after ORDER_TIMEOUT
        check_order.apply_async(
            args=[bundle.obj.id, ],
            countdown=settings.ORDER_TIMEOUT,
        )

        return bundle
