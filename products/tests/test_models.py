from django.test import TestCase
from model_mommy import mommy

from products.models import Product, Order, OrderProduct


class ProductTests(TestCase):

    def test_save_product(self):
        product = mommy.make('Product')
        product.save()

        self.assertTrue(isinstance(product, Product))

    def test_update_product(self):
        product = mommy.make('Product', name='name')
        product.name = 'changed name'
        product.save()

        self.assertEquals(
            product.name, Product.objects.get(pk=product.pk).name
        )

    def test_delete_product(self):
        product = mommy.make('Product')
        product.save()

        product.delete()

        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=product.pk)

    def test_enough_stock(self):
        product = mommy.make('Product', stock=10)
        self.assertTrue(product.enough_stock(5))

    def test_not_enough_stock(self):
        product = mommy.make('Product', stock=10)
        self.assertFalse(product.enough_stock(20))


class OrderTests(TestCase):

    def test_save_order(self):
        order = mommy.make('Order')
        order.save()

        self.assertTrue(isinstance(order, Order))

    def test_order_defaults_as_not_complete(self):
        order = Order()
        order.save()

        self.assertFalse(Order.objects.get(id=order.id).complete)

    def test_update_order(self):
        order = mommy.make('Order', complete=False)
        order.complete = True
        order.save()

        self.assertTrue(Order.objects.get(pk=order.pk).complete)

    def test_delete_order(self):
        order = mommy.make('Order')
        order.save()

        order.delete()

        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(pk=order.pk)


class OrderProductTests(TestCase):

    def test_save_order_product(self):
        order_product = mommy.make('OrderProduct')
        order_product.save()

        self.assertTrue(isinstance(order_product, OrderProduct))

    def test_update_order_product(self):
        order_product = mommy.make('OrderProduct', quantity=10)
        order_product.quantity = 5
        order_product.save()

        self.assertEquals(
            OrderProduct.objects.get(pk=order_product.pk).quantity, 5
        )

    def test_delete_order_product(self):
        order_product = mommy.make('OrderProduct')
        order_product.save()

        order_product.delete()

        with self.assertRaises(OrderProduct.DoesNotExist):
            OrderProduct.objects.get(pk=order_product.pk)
