from django.shortcuts import render
from django.views import generic

# Create your views here.

class HomePageView(generic.TemplateView):
    template_name = 'common/homepage.html'

class AboutView(generic.TemplateView):
    template_name = 'common/about.html'

