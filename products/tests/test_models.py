from django.core.cache import cache
from django.test import TestCase
from model_mommy import mommy
from mock import patch, ANY

from products.models import Product, Order, OrderProduct


class ProductTests(TestCase):

    def tearDown(self):
        """ Make sure cache is empty before every test """
        cache.clear()

    def test_save_product(self):
        """ Test saving a new product  """
        product = mommy.make('Product')
        self.assertTrue(isinstance(product, Product))

    def test_update_product(self):
        """ Test updating the name of a product """
        product = mommy.make('Product', name='name')
        product.name = 'changed name'
        product.save()

        self.assertEquals(
            product.name, Product.objects.get(pk=product.pk).name
        )

    def test_delete_product(self):
        """ Test delete of a product """
        product = mommy.make('Product')
        product.delete()

        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=product.pk)

    def test_enough_stock(self):
        """ Test model has enough stock """
        product = mommy.make('Product', stock=10)
        self.assertTrue(product.enough_stock(5))

    def test_not_enough_stock(self):
        """ Test model does not have enough stock """
        product = mommy.make('Product', stock=10)
        self.assertFalse(product.enough_stock(20))

    def test_real_stock(self):
        """ Test real stock works well when no reserved items """
        product = mommy.make('Product', stock=10)
        self.assertEquals(product.real_stock, 10)

    def test_reserve_stock_sets_cache(self):
        """ Test reserving stock for the first time calls cache.set """
        product = mommy.make('Product', stock=10)

        with patch('django.core.cache.cache.set') as cache_mock:
            product.reserve_stock(5)
            cache_mock.assert_called_once_with(ANY, 5)

    def test_reserve_stock_increments_cache(self):
        """ Test reserving stock for the second time calls cache.incr """
        product = mommy.make('Product', stock=10)
        product.reserve_stock(5)

        with patch('django.core.cache.cache.incr') as cache_mock:
            product.reserve_stock(3)
            cache_mock.assert_called_once_with(ANY, 3)

    def test_reserve_stock(self):
        """ Test real stock is updated after reserving items """
        product = mommy.make('Product', stock=10)
        product.reserve_stock(5)

        self.assertEquals(product.real_stock, 5)

    def test_reserve_more_stock(self):
        """ Test real stock is updated when reserving multiple times """
        product = mommy.make('Product', stock=10)
        product.reserve_stock(3)
        product.reserve_stock(2)

        self.assertEquals(product.real_stock, 5)

    def test_reserve_stock_too_much(self):
        """ Test exception is thrown when traying to reserve too much """
        product = mommy.make('Product', stock=10)

        with self.assertRaises(ValueError):
            product.reserve_stock(15)

    def test_reserve_stock_not_a_number(self):
        """ Test exception is thrown when traying to reserve not an integer """
        product = mommy.make('Product', stock=10)

        with self.assertRaises(ValueError):
            product.reserve_stock("foo")

    def test_release_stock(self):
        """ Test real stock is updated when release stock """
        product = mommy.make('Product', stock=10)
        product.reserve_stock(5)
        product.release_stock(2)

        self.assertEquals(product.real_stock, 7)

    def test_release_stock_decrements_cache(self):
        """ Test releasing stock calls cache.decr """
        product = mommy.make('Product', stock=10)
        product.reserve_stock(5)

        with patch('django.core.cache.cache.decr') as cache_mock:
            product.release_stock(3)
            cache_mock.assert_called_once_with(ANY, 3)

    def test_release_stock_too_much(self):
        """
        Test exception is raised when trying to release more than reserved
        """
        product = mommy.make('Product', stock=10)
        product.reserve_stock(5)

        with self.assertRaises(ValueError):
            product.release_stock(7)

    def test_release_stock_not_a_number(self):
        """ Test exception is raised when trying to release not an integer """
        product = mommy.make('Product', stock=10)

        with self.assertRaises(ValueError):
            product.release_stock("bar")


class OrderTests(TestCase):

    def test_save_order(self):
        """ Test saving a new order """
        order = mommy.make('Order')
        self.assertTrue(isinstance(order, Order))

    def test_order_defaults_as_not_complete(self):
        """ Test orders are created as not complete by default """
        order = Order()
        order.save()

        self.assertFalse(Order.objects.get(id=order.id).complete)

    def test_update_order(self):
        """ Test updating the complete stated of an order """
        order = mommy.make('Order', complete=False)
        order.complete = True
        order.save()

        self.assertTrue(Order.objects.get(pk=order.pk).complete)

    def test_delete_order(self):
        """ Test deleting an order """
        order = mommy.make('Order')
        order.delete()

        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(pk=order.pk)

    def test_delete_order_cascade(self):
        """ Test deleting an order deletes its relationships """
        order = mommy.make('Order')
        product = mommy.make('Product')

        order_product = mommy.make('OrderProduct',
                                   order=order,
                                   product=product)

        order.delete()
        with self.assertRaises(OrderProduct.DoesNotExist):
            OrderProduct.objects.get(id=order_product.id)


class OrderProductTests(TestCase):

    def test_save_order_product(self):
        """ Test creating a new order product """
        order_product = mommy.make('OrderProduct')

        self.assertTrue(isinstance(order_product, OrderProduct))

    def test_update_order_product(self):
        """ Test updating a new order product """
        order_product = mommy.make('OrderProduct', quantity=10)
        order_product.quantity = 5
        order_product.save()

        self.assertEquals(
            OrderProduct.objects.get(pk=order_product.pk).quantity, 5
        )

    def test_delete_order_product(self):
        """ Test deleting an order product """
        order_product = mommy.make('OrderProduct')
        order_product.delete()

        with self.assertRaises(OrderProduct.DoesNotExist):
            OrderProduct.objects.get(pk=order_product.pk)

    def test_price(self):
        """
        Test price takes into account both unitary products as well as
        'weighted' products
        """
        price_1 = 1
        price_2 = 2
        quantity_1 = 1
        quantity_2 = 200

        product_1 = mommy.make('Product', price=price_1, unitary=True)
        product_2 = mommy.make('Product', price=price_2, unitary=False)

        order = mommy.make('Order')
        mommy.make('OrderProduct', product=product_1, order=order,
                   quantity=quantity_1)
        mommy.make('OrderProduct', product=product_2, order=order,
                   quantity=quantity_2)

        price = (quantity_1 * price_1) + ((quantity_2 / 100) * price_2)
        self.assertEquals(price, order.price())

    def test_price_discount_multiple_products(self):
        """
        Test price correctly applies 3x2 discount when appropiate, if you take
        8 products, you should only pay for 6 (two times the promotion)
        """
        price_1 = 1
        quantity_1 = 8

        product_1 = mommy.make('Product', price=price_1, unitary=True)

        order = mommy.make('Order')
        mommy.make('OrderProduct', product=product_1, order=order,
                   quantity=quantity_1)

        price = ((quantity_1 - 2) * price_1)  # Two times 3x2 promotion
        self.assertEquals(price, order.price())

    def test_price_discount_full_menu(self):
        """
        Test price correctly applies the full menu discount when taking
        products from all possible categories
        """
        order = mommy.make('Order')

        total_price = 0
        for category in Product.CATEGORY_CHOICES:
            product = mommy.make('Product', category=category[0],
                                 unitary=False)
            order_product = mommy.make('OrderProduct', order=order,
                                       product=product)

            total_price += (product.price * (order_product.quantity / 100))

        total_price *= 0.8  # Full menu discount should have been applied
        self.assertEquals(order.price(), total_price)
