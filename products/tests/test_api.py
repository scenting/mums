import json
from django.test import TestCase
from django.test.client import Client
from model_mommy import mommy
from tastypie.test import ResourceTestCaseMixin

from products.models import Product, Order, OrderProduct


class ProductResourceTests(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        self.c = Client()

        self.default_products = Product.objects.all().count()

    def test_get_list(self):
        mommy.make('Product', _quantity=10)
        total_products = self.default_products + 10

        response = self.c.get('/api/v1/product/')
        self.assertHttpOK(response)

        body = json.loads(response.content.decode())
        self.assertEquals(body['meta']['total_count'], total_products)

    def test_get_list_limit(self):
        response = self.c.get('/api/v1/product/?limit=3')
        self.assertHttpOK(response)

        body = json.loads(response.content.decode())
        self.assertEquals(body['meta']['total_count'], self.default_products)
        self.assertEquals(len(body['objects']), 3)

    def test_get_list_pagination(self):
        response = self.c.get('/api/v1/product/?limit=3')
        self.assertHttpOK(response)

        body = json.loads(response.content.decode())
        first_ids = [obj['id'] for obj in body['objects']]

        response = self.c.get(body['meta']['next'])
        self.assertHttpOK(response)

        body = json.loads(response.content.decode())
        second_ids = [obj['id'] for obj in body['objects']]

        self.assertEquals(len(set(first_ids)), 3)
        self.assertEquals(len(set(second_ids)), 3)
