# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-24 18:59
from __future__ import unicode_literals

from django.db import migrations


def initial_stock(apps, schema_editor):
    Product = apps.get_model('products', 'Product')

    for product in Product.objects.all():
        if product.unitary:
            product.stock = 10
        else:
            product.stock = 1000
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_stock'),
    ]

    operations = [
        migrations.RunPython(initial_stock)
    ]
