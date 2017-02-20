from django.conf.urls import url
from . import views

app_name = 'common'

urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name='index'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
]

