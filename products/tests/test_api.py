import json
from django.core.cache import cache
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from mock import patch
from model_mommy import mommy
from tastypie.test import ResourceTestCaseMixin

from products.models import Product


class ProductResourceTests(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        self.c = Client()

        self.default_products = Product.objects.all().count()

    def test_get_list(self):
        """ Test getting a list of products """
        mommy.make('Product', _quantity=10)

        response = self.c.get('/api/v1/product/')
        self.assertHttpOK(response)

    def test_get_list_limit(self):
        """ Test get a limited list """
        response = self.c.get('/api/v1/product/?limit=3')
        self.assertHttpOK(response)

        body = json.loads(response.content.decode())
        self.assertEquals(len(body['objects']), 3)

    def test_get_list_pagination(self):
        """ Test pagination, ids should not be duplicated """
        response = self.c.get('/api/v1/product/?limit=3')
        self.assertHttpOK(response)

        ids = set()

        body = json.loads(response.content.decode())
        ids.update([obj['id'] for obj in body['objects']])

        response = self.c.get(body['meta']['next'])
        self.assertHttpOK(response)

        body = json.loads(response.content.decode())
        ids.update([obj['id'] for obj in body['objects']])

        self.assertEquals(len(ids), 6)

    def test_get_detail(self):
        """ Test getting a product detail """
        product = Product.objects.first()

        response = self.c.get('/api/v1/product/{}/'.format(product.id))
        self.assertHttpOK(response)

    def test_post_not_allowed(self):
        """ Test POST method is not allowed """
        product = Product.objects.first()

        response = self.c.post('/api/v1/product/{}/'.format(product.id))
        self.assertHttpMethodNotAllowed(response)

    def test_patch_not_allowed(self):
        """ Test PATCH method is not allowed """
        product = Product.objects.first()

        response = self.c.patch('/api/v1/product/{}/'.format(product.id))
        self.assertHttpMethodNotAllowed(response)

    def test_delete_not_allowed(self):
        """ Test DELETE method is not allowed """
        product = Product.objects.first()

        response = self.c.delete('/api/v1/product/{}/'.format(product.id))
        self.assertHttpMethodNotAllowed(response)


class OrderResourceTests(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        self.c = Client()

    def tearDown(self):
        """ Make sure cache is empty before every test """
        cache.clear()

    def test_get_list(self):
        """ Test getting a list of orders """
        mommy.make('Order', _quantity=10)

        response = self.c.get('/api/v1/order/')
        self.assertHttpOK(response)

    def test_get_list_limit(self):
        """ Test get a limited list """
        mommy.make('Order', _quantity=10)
        response = self.c.get('/api/v1/order/?limit=3')
        self.assertHttpOK(response)

        body = json.loads(response.content.decode())
        self.assertEquals(len(body['objects']), 3)

    def test_get_list_pagination(self):
        """ Test pagination, ids should not be duplicated """
        mommy.make('Order', _quantity=10)
        response = self.c.get('/api/v1/order/?limit=3')
        self.assertHttpOK(response)

        ids = set()

        body = json.loads(response.content.decode())
        ids.update([obj['id'] for obj in body['objects']])

        response = self.c.get(body['meta']['next'])
        self.assertHttpOK(response)

        body = json.loads(response.content.decode())
        ids.update([obj['id'] for obj in body['objects']])

        self.assertEquals(len(ids), 6)

    def test_get_detail(self):
        """ Test getting a order detail """
        order = mommy.make('Order')

        response = self.c.get('/api/v1/order/{}/'.format(order.id))
        self.assertHttpOK(response)

    def test_patch_detail(self):
        """ Test patching an order as completed """
        order = mommy.make('Order', complete=False)

        response = self.c.patch(
            '/api/v1/order/{}/'.format(order.id),
            json.dumps({'complete': True}),
            content_type='application/json'
        )
        self.assertHttpAccepted(response)

    @patch.object(Product, 'release_stock')
    def test_patch_stock_is_released(self, release_mock):
        """ Test the reserved stock is released when an order is completed """
        order = mommy.make('Order', complete=False)
        product = mommy.make('Product')
        order_product = mommy.make('OrderProduct', order=order,
                                   product=product)

        response = self.c.patch(
            '/api/v1/order/{}/'.format(order.id),
            json.dumps({'complete': True}),
            content_type='application/json'
        )
        self.assertHttpAccepted(response)
        release_mock.assert_called_once_with(order_product.quantity)

    def test_patch_stock_is_consolidated(self):
        """
        Test the reserved stock is consolidated when an order is completed
        """
        order = mommy.make('Order', complete=False)
        product = mommy.make('Product', stock=10)

        mommy.make('OrderProduct', order=order, product=product, quantity=5)
        product.reserve_stock(5)

        response = self.c.patch(
            '/api/v1/order/{}/'.format(order.id),
            json.dumps({'complete': True}),
            content_type='application/json'
        )
        self.assertHttpAccepted(response)
        self.assertEquals(Product.objects.get(id=product.id).stock, 5)

    def test_post(self):
        """ Test POST a new order """
        product = mommy.make('Product', stock=10)

        response = self.c.post(
            '/api/v1/order/',
            json.dumps({'products': [{'product': product.id, 'quantity': 1}]}),
            content_type='application/json'
        )
        self.assertHttpCreated(response)

    def test_post_not_enough_stock(self):
        """ Test POST fails when not enough stock of the product """
        product = mommy.make('Product', stock=0)

        response = self.c.post(
            '/api/v1/order/',
            json.dumps({'products': [{'product': product.id, 'quantity': 1}]}),
            content_type='application/json'
        )
        self.assertHttpBadRequest(response)

    def test_post_invalid_product(self):
        """
        Test POST fails with 404 when the product requested does not exist
        """
        product = mommy.make('Product', stock=0)
        product.delete()

        response = self.c.post(
            '/api/v1/order/',
            json.dumps({'products': [{'product': product.id, 'quantity': 1}]}),
            content_type='application/json'
        )
        self.assertHttpNotFound(response)

    def test_post_invalid_data(self):
        """ Test POST fails when the data is incorrectly formed """
        mommy.make('Product', stock=0)

        response = self.c.post(
            '/api/v1/order/',
            json.dumps({"foo": "bar"}),
            content_type='application/json'
        )
        self.assertHttpBadRequest(response)

    @patch.object(Product, 'reserve_stock')
    def test_post_stock_is_reserved(self, reserve_mock):
        """ Test POST reserve the requested product stock """
        product = mommy.make('Product', stock=10)

        response = self.c.post(
            '/api/v1/order/',
            json.dumps({'products': [{'product': product.id, 'quantity': 1}]}),
            content_type='application/json'
        )
        self.assertHttpCreated(response)
        reserve_mock.assert_called_once_with(1)

    @patch('products.tasks.check_order.apply_async')
    def test_post_task_is_scheduled(self, task_mock):
        """ Test POST schedule the task to check if the order has been paid """
        product = mommy.make('Product', stock=10)

        response = self.c.post(
            '/api/v1/order/',
            json.dumps({'products': [{'product': product.id, 'quantity': 1}]}),
            content_type='application/json'
        )
        self.assertHttpCreated(response)
        body = json.loads(response.content.decode())

        order_id = body['id']
        task_mock.assert_called_once_with(
            args=[order_id, ], countdown=settings.ORDER_TIMEOUT
        )

    def test_get_list_number_of_queries(self):
        """ Test the number of queries required to list a group of orders """
        products = mommy.make('Product', _quantity=10)

        for order in mommy.make('Order', _quantity=10):
            for product in products:
                mommy.make('OrderProduct', order=order, product=product)

        with self.assertNumQueries(1):
            self.assertHttpOK(self.c.get('/api/v1/order/'))
