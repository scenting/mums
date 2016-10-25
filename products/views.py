from django.shortcuts import render
from .models import Product, Order


def index(request):
    context = {
        'products': Product.objects.all(),
    }
    return render(request, 'products/index.html', context)


def new_order(request):
    print('new_order')
