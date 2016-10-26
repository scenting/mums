from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext as _


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

    # TODO: Add validator for price < 0
    price = models.FloatField(_(u'Price'))

    category = models.PositiveSmallIntegerField(_(u'Category'),
                                                choices=CATEGORY_CHOICES)

    unitary = models.BooleanField(_(u'Is unitary'), default=True)

    stock = models.IntegerField(_(u'Stock'), default=0)

    @property
    def reserved(self):
        return cache.get(self._get_redis_key()) or 0

    @property
    def real_stock(self):
        return self.stock - self.reserved

    def enough_stock(self, quantity):
        return self.real_stock > quantity

    def reserve_stock(self, quantity):
        if not isinstance(quantity, int) or not self.enough_stock(quantity):
            raise ValueError('Not enough stock')

        try:
            cache.incr(self._get_redis_key(), quantity)
        except ValueError:
            cache.set(self._get_redis_key(), quantity)

    def release_stock(self, quantity):
        if not isinstance(quantity, int) or quantity > self.reserved:
            raise ValueError('Not that much stock is reserved')

        cache.decr(self._get_redis_key(), quantity)

    def _get_redis_key(self):
        return 'product_#{}'.format(self.id)


class Order(models.Model):

    created = models.DateTimeField(_(u'Creation date'), auto_now_add=True,
                                   db_index=True)

    complete = models.BooleanField(_(u'Is complete'), default=False)

    products = models.ManyToManyField(Product, through='OrderProduct',
                                      related_name='order_products')


class OrderProduct(models.Model):
    order = models.ForeignKey(Order)

    product = models.ForeignKey(Product)

    quantity = models.IntegerField(_(u'Quantity'))
