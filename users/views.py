from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import SignupForm, SigninForm
from .utils import FormHandlerMixin
from django.contrib import messages

class SignupView(FormHandlerMixin, View):
    form_class = SignupForm
    template_name = 'users/signup.html'

    def handle_form(self, request, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(request, user)
        return redirect(self.success_url)

class SigninView(FormHandlerMixin, View):
    form_class = SigninForm
    template_name = 'users/signin.html'

    def handle_form(self, request, form):
        phone = form.cleaned_data['phone']
        password = form.cleaned_data['password']
        user = authenticate(request, phone=phone, password=password)
        if user is not None:
            login(request, user)
            return redirect(self.success_url)
        else:
            messages.error(request, 'Неверный номер телефона или пароль.')
            return render(request, self.template_name, {'form': form})