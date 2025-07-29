from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.conf import settings
import uuid
import secrets
from django.utils import timezone
from django.core.mail import send_mail

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.verification_token = secrets.token_urlsafe(32)  # Более безопасный токен

        if commit:
            user.save()
            self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        verification_url = reverse_lazy("verify", args=[user.verification_token])
        subject = "Подтверждение регистрации"
        message = f"Для подтверждения email перейдите по ссылке:\n\n{settings.BASE_URL}{verification_url}"
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Ошибка отправки email: {e}")


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        context["user"].reset_token = secrets.token_urlsafe(32)
        context["user"].reset_token_created = timezone.now()
        context["user"].save()

        reset_url = reverse_lazy(
            "password_reset_confirm", args=[context["user"].reset_token]
        )
        subject = "Восстановление пароля"
        message = f"Для восстановления пароля перейдите по ссылке:\n\n{settings.BASE_URL}{reset_url}"
        send_mail(
            subject,
            message,
            from_email,
            [to_email],
            fail_silently=False,
        )


class CustomSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        user = super().save(commit=commit)
        user.reset_token = None
        user.reset_token_created = None
        if commit:
            user.save()
        return user
