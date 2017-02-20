from django.shortcuts import render
from django.views.generic import TemplateView, View, FormView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm

# Create your views here.
class LoginView(FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get(self, request):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = {'form': form}
        if 'next' in request.GET:
            context['next'] = request.GET['next']
        return render(request, self.template_name, context)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        next = request.POST['next']
        user = authenticate(email=email, password=password)
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if user is not None:
            if user.is_active:
                login(request, user)
                if next != '':
                    return HttpResponseRedirect(request.POST['next'])
                else:
                    return HttpResponseRedirect('orders:list')
            else:
                return HttpResponse("Inactive user.")
        else:
            return render(request, self.template_name, {'form': form})

        # return render(request, "index.html")

class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')