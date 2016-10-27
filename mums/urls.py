import debug_toolbar
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from tastypie.api import Api

from products.api.resources_v1 import OrderResource, ProductResource, \
    OrderProductResource
from products.views import index, new_order
from products.utils import debug


v1_api = Api(api_name='v1')
v1_api.register(OrderResource())
v1_api.register(ProductResource())
v1_api.register(OrderProductResource())

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^new_order/$', new_order, name='new_order'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^debug/', debug),
    ]
