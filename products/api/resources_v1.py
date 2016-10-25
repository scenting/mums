from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.http import HttpBadRequest
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import fields
from django.shortcuts import get_object_or_404
from products.models import Product, Order, OrderProduct


class ProductResource(ModelResource):

    class Meta(object):
        queryset = Product.objects.all()
        resource_name = 'product'
        # TODO: allow only GET


class OrderProductResource(ModelResource):

    class Meta(object):
        queryset = OrderProduct.objects.all()
        resource_name = 'order_product'
        # TODO: allow only GET


class OrderResource(ModelResource):

    products = fields.ToManyField(OrderProductResource, 'orderproduct_set',
                                  full=True)

    class Meta(object):
        queryset = Order.objects.all()
        resource_name = 'order'
        always_return_data = True
        authorization = Authorization()
        # TODO: allow only GET, POST, PATCH

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
