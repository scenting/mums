from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Product, Order


def index(request):
    context = {
        'products': Product.objects.all(),
    }
    return render(request, 'products/index.html', context)


def new_order(request):
    order = get_object_or_404(Order, pk=request.GET.get('order'))

    context = {
        'order': order,
        'products': order.products.all(),
        'timeout': settings.ORDER_TIMEOUT
    }

    return render(request, 'products/new_order.html', context)
