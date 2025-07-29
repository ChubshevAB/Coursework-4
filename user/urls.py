from django.urls import path
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView,
    VerifyEmailView,
    CustomLoginView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    logout_view,
    UserListView,
    UserUpdateView
)

urlpatterns = [
    # Аутентификация
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<str:token>/', VerifyEmailView.as_view(), name='verify'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

    # Сброс пароля (исправленные пути)
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             success_url=reverse_lazy('password_reset_done')
         ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
]
