from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Product, Order


def index(request):
    context = {
        'products': Product.objects.all(),
    }
    return render(request, 'products/index.html', context)


def new_order(request):
    order = get_object_or_404(Order, pk=request.GET.get('order'))

    context = {
        'order': order.id,
        'products': order.products.all(),
    }

    return render(request, 'products/new_order.html', context)
