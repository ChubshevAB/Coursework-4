from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.views.generic import ListView, UpdateView

from .forms import RegisterForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import User
from django.contrib import messages
from django.urls import reverse_lazy


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация успешна! Проверьте ваш email для подтверждения.')
            return redirect('login')
        return render(request, 'registration/register.html', {'form': form})


class VerifyEmailView(View):
    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            user.is_verified = True
            user.verification_token = None
            user.save()
            messages.success(request, 'Email успешно подтверждён! Теперь вы можете войти.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Неверная ссылка подтверждения.')
            return redirect('home')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset.html'
    success_url = reverse_lazy('login')
    email_template_name = 'registration/password_reset_email.html'

    def form_valid(self, form):
        messages.success(self.request, 'Инструкции по восстановлению пароля отправлены на ваш email.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменён! Теперь вы можете войти.')
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')


class UserListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = User
    template_name = 'user/user_list.html'
    context_object_name = 'users'
    permission_required = 'user.view_all_users'
    login_url = reverse_lazy('login')

class UserUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'user/user_edit.html'
    fields = ['username', 'email', 'is_active', 'is_staff']
    success_url = reverse_lazy('user-list')
    permission_required = 'user.change_user'
    login_url = reverse_lazy('login')