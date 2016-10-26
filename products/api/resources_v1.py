import json
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.http import HttpBadRequest
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import fields
from django.shortcuts import get_object_or_404
from products.models import Product, Order, OrderProduct


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


class OrderResource(ModelResource):

    # TODO: prefetch related
    products = fields.ToManyField(OrderProductResource, 'orderproduct_set',
                                  full=True)

    class Meta(object):
        queryset = Order.objects.all()
        resource_name = 'order'
        always_return_data = True
        authorization = Authorization()
        authentication = Authentication()
        allowed_methods = ['get', 'post', 'patch', ]

    def obj_update(self, bundle, **kwargs):
        body = json.loads(bundle.request.body.decode())

        if body.get('complete'):
            bundle.obj.complete = True
            bundle.obj.save()

    def obj_create(self, bundle, **kwargs):
        if not bundle.data.get('products'):
            raise ImmediateHttpResponse(HttpBadRequest('No products provided'))

        for product_row in bundle.data.get('products'):
            product = get_object_or_404(Product, pk=product_row.get('product'))
            if not product.enough_stock(product_row.get('quantity')):
                raise ImmediateHttpResponse(HttpBadRequest('Not enough stock'))

        # It's already validated
        bundle.obj.save()

        for product_row in bundle.data.get('products'):
            OrderProduct(
                order_id=bundle.obj.id,
                product_id=product_row.get('product'),
                quantity=product_row.get('quantity')
            ).save()

        return bundle
