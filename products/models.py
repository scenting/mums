from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext as _
from math import floor


class Product(models.Model):

    CATEGORY_PRINCIPAL = 0
    CATEGORY_BEVERAGE = 1
    CATEGORY_DESSERT = 2

    CATEGORY_CHOICES = (
        (CATEGORY_PRINCIPAL, _('Pricipal')),
        (CATEGORY_BEVERAGE, _('Beverage')),
        (CATEGORY_DESSERT, _('Dessert')),
    )

    name = models.CharField(_(u'Name'), max_length=256)

    price = models.FloatField(_(u'Price'))

    category = models.PositiveSmallIntegerField(_(u'Category'),
                                                choices=CATEGORY_CHOICES)

    unitary = models.BooleanField(_(u'Is unitary'), default=True)

    stock = models.IntegerField(_(u'Stock'), default=0)

    @property
    def reserved(self):
        """ Check the amount reserved but not yet paid using redis """
        return cache.get(self._get_redis_key()) or 0

    @property
    def real_stock(self):
        """ Get the 'real' stock as current stock minus reserved items """
        return self.stock - self.reserved

    def enough_stock(self, quantity):
        """ Check if there is enough stock to make a sale """
        return self.real_stock >= quantity

    def reserve_stock(self, quantity):
        """ Mark quantity as reserved but not yet paid """
        if not isinstance(quantity, int) or not self.enough_stock(quantity):
            raise ValueError('Not enough stock')

        try:
            cache.incr(self._get_redis_key(), quantity)
        except ValueError:
            cache.set(self._get_redis_key(), quantity)

    def release_stock(self, quantity):
        """ Mark quantity as no longed reserved """
        if not isinstance(quantity, int) or quantity > self.reserved:
            raise ValueError('Not that much stock is reserved')

        cache.decr(self._get_redis_key(), quantity)

    def _get_redis_key(self):
        """ Get redis unique product token """
        return 'product_#{}'.format(self.id)


class Order(models.Model):

    created = models.DateTimeField(_(u'Creation date'), auto_now_add=True,
                                   db_index=True)

    complete = models.BooleanField(_(u'Is complete'), default=False)

    products = models.ManyToManyField(Product, through='OrderProduct',
                                      related_name='order_products')

    def price(self):
        """
        Gets the total price of an order taking into consideration the price
        scheme of each product (unitary or not) as well as applying the
        appropiate discounts:
            - 3x2 offer: Get 3 pay 2 (only on unitary products)
            - Full menu: Get 20% off when buying products from every category
        """
        total_price = 0

        order_categories = set()

        for order_product in self.orderproduct_set.all():
            price = order_product.product.price
            quantity = order_product.quantity

            order_categories.add(order_product.product.category)

            if not order_product.product.unitary:
                quantity /= 100  # Price scheme is by €/100gr
            else:
                # Apply discount for 3x2 promotion on unitary products
                quantity -= floor(quantity / 3)

            total_price += price * quantity

        # Apply discount for full_menu (20%)
        if len(order_categories) == len(Product.CATEGORY_CHOICES):
            total_price *= 0.8

        return total_price


class OrderProduct(models.Model):
    order = models.ForeignKey(Order)

    product = models.ForeignKey(Product)

    quantity = models.PositiveIntegerField(_(u'Quantity'))
