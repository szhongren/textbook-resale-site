from django.conf.urls import url
from . import views

app_name = 'books'

urlpatterns = [
    url(r'^$', views.BookSearchView.as_view(), name='search'),
    url(r'^(?P<pk>\d{9}[\d|X])/', views.BookView.as_view(), name='detail'),

]