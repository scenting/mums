"""mums URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from products.api.resources_v1 import OrderResource, ProductResource, \
    OrderProductResource
from products.views import index, new_order
from tastypie.api import Api


v1_api = Api(api_name='v1')
v1_api.register(OrderResource())
v1_api.register(ProductResource())
v1_api.register(OrderProductResource())

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^new_order$', new_order, name='new_order'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
