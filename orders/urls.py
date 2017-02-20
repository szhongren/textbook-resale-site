from django.conf.urls import url
from . import views

app_name = 'orders'

urlpatterns = [
    url(r'^$', views.OrderListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/', views.OrderDetailView.as_view(), name='detail'),
    url(r'^create/$', views.OrderCreateView.as_view(), name='create'),
    url(r'^confirm/$', views.OrderConfirmView.as_view(), name='confirm'),
]