# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-27 11:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20161025_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='quantity',
            field=models.PositiveIntegerField(verbose_name='Quantity'),
        ),
    ]