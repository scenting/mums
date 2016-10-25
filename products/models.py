from django.db import models
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

    def enough_stock(self, quantity):
        return True


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
