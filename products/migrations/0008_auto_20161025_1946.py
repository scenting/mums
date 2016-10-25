# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 19:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20161024_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(related_name='order_products', through='products.OrderProduct', to='products.Product'),
        ),
    ]