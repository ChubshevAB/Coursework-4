from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from user.forms import RegisterForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy

from user.models import User
from .models import Recipient, Message, Mailing, MailingAttempt
import logging
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache


# Модель 'Получатель'
@method_decorator(cache_page(60 * 15), name='dispatch')
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = "mailing/recipient_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("recipient-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    template_name = "mailing/recipient_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("recipient-list")

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("recipient-list")

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


# Модель 'Сообщение'
@method_decorator(cache_page(60 * 15), name='dispatch')
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ["title", "letter"]
    success_url = reverse_lazy("message-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ["title", "letter"]
    success_url = reverse_lazy("message-list")

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("message-list")

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


# Модель 'Рассылка'
@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 10
    ordering = ["-first_datetime"]

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    template_name = "mailing/mailing_form.html"
    fields = ["first_datetime", "end_datetime", "status", "message", "recipients"]
    success_url = reverse_lazy("mailing-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user

        # Проверяем, что сообщение принадлежит текущему пользователю
        message = form.cleaned_data.get('message')
        if message and message.owner != self.request.user:
            form.add_error('message', 'Вы не можете использовать это сообщение')
            return self.form_invalid(form)

        # Проверяем, что все получатели принадлежат текущему пользователю
        recipients = form.cleaned_data.get('recipients')
        if recipients:
            invalid_recipients = recipients.exclude(owner=self.request.user)
            if invalid_recipients.exists():
                form.add_error('recipients', 'Вы не можете использовать этих получателей')
                return self.form_invalid(form)

        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Фильтруем queryset для message и recipients
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=self.request.user)
        return form


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    template_name = "mailing/mailing_form.html"
    fields = ["first_datetime", "end_datetime", "status", "message", "recipients"]
    success_url = reverse_lazy("mailing-list")

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def form_valid(self, form):
        # Проверяем, что сообщение принадлежит текущему пользователю
        message = form.cleaned_data.get('message')
        if message and message.owner != self.request.user:
            form.add_error('message', 'Вы не можете использовать это сообщение')
            return self.form_invalid(form)

        # Проверяем, что все получатели принадлежат текущему пользователю
        recipients = form.cleaned_data.get('recipients')
        if recipients:
            invalid_recipients = recipients.exclude(owner=self.request.user)
            if invalid_recipients.exists():
                form.add_error('recipients', 'Вы не можете использовать этих получателей')
                return self.form_invalid(form)

        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Фильтруем queryset для message и recipients
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=self.request.user)
        return form


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing-list")

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


# Модель 'Попытка рассылки'
@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/attempt_list.html"
    context_object_name = "attempts"
    paginate_by = 20
    ordering = ["-attempt_datetime"]

    def get_queryset(self):
        queryset = super().get_queryset().filter(mailing__owner=self.request.user)
        mailing_id = self.request.GET.get('mailing_id')
        if mailing_id:
            queryset = queryset.filter(mailing_id=mailing_id)
        return queryset


def start_mailing(mailing_id):
    logger = logging.getLogger(__name__)

    try:
        mailing = Mailing.objects.get(id=mailing_id)
        recipients = mailing.recipients.all()

        all_successful = True
        total_recipients = recipients.count()
        success_count = 0
        failed_count = 0

        if total_recipients == 0:
            mailing.status = 'completed'
            mailing.save()
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'all_successful': True,
                'status': 'completed',
                'message': 'Нет получателей для рассылки'
            }

        for recipient in recipients:
            try:
                send_mail(
                    subject=mailing.message.title,
                    message=mailing.message.letter,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False
                )

                MailingAttempt.objects.create(
                    status='success',
                    mailing=mailing,
                    recipient=recipient,
                    server_response='Письмо успешно отправлено',
                    owner=mailing.owner
                )
                success_count += 1

            except Exception as e:
                logger.error(f"Ошибка отправки письма для {recipient.email}: {str(e)}")

                MailingAttempt.objects.create(
                    status='failed',
                    mailing=mailing,
                    recipient=recipient,
                    server_response=str(e),
                    owner=mailing.owner
                )
                all_successful = False
                failed_count += 1

        mailing.status = 'completed' if all_successful else 'started'
        mailing.save()

        result = {
            'total': total_recipients,
            'success': success_count,
            'failed': failed_count,
            'all_successful': all_successful,
            'status': mailing.status,
            'message': 'Рассылка завершена успешно' if all_successful else 'Рассылка завершена с ошибками'
        }

        return result

    except Mailing.DoesNotExist:
        logger.error(f"Рассылка с ID {mailing_id} не найдена")
        return {
            'status': 'error',
            'message': f'Рассылка с ID {mailing_id} не найдена'
        }
    except Exception as e:
        logger.error(f"Ошибка при выполнении рассылки: {str(e)}")
        return {
            'status': 'error',
            'message': f'Произошла ошибка: {str(e)}'
        }


def home_view(request):
    if request.user.is_authenticated:
        context = {
            'total_mailings': Mailing.objects.filter(owner=request.user).count(),
            'active_mailings': Mailing.objects.filter(owner=request.user, status='started').count(),
            'unique_recipients': Recipient.objects.filter(owner=request.user).distinct().count(),
        }
    else:
        context = {
            'total_mailings': 0,
            'active_mailings': 0,
            'unique_recipients': 0,
        }
    return render(request, 'mailing/base.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class StartMailingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            from .models import Mailing
            mailing = Mailing.objects.get(id=pk, owner=request.user)

            if mailing.status == 'completed':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Рассылка уже завершена'
                }, status=400)

            # Запускаем рассылку
            start_mailing(pk)

            return JsonResponse({
                'status': 'success',
                'message': 'Рассылка успешно запущена'
            })

        except Mailing.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Рассылка не найдена'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


# Moderator Views
class AllMailingsListView(PermissionRequiredMixin, ListView):
    permission_required = 'mailing.view_all_mailings'
    model = Mailing
    template_name = "mailing/all_mailings_list.html"
    context_object_name = "mailings"
    paginate_by = 20
    ordering = ["-first_datetime"]

    def get_queryset(self):
        return super().get_queryset().select_related('owner', 'message')

class AllMessagesListView(PermissionRequiredMixin, ListView):
    permission_required = 'mailing.view_all_messages'
    model = Message
    template_name = "mailing/all_messages_list.html"
    context_object_name = "messages"
    paginate_by = 20
    ordering = ["-id"]

    def get_queryset(self):
        return super().get_queryset().select_related('owner')

class AllRecipientsListView(PermissionRequiredMixin, ListView):
    permission_required = 'mailing.view_all_recipients'
    model = Recipient
    template_name = "mailing/all_recipients_list.html"
    context_object_name = "recipients"
    paginate_by = 20
    ordering = ["email"]

    def get_queryset(self):
        return super().get_queryset().select_related('owner')

class AllAttemptsListView(PermissionRequiredMixin, ListView):
    permission_required = 'mailing.view_all_attempts'
    model = MailingAttempt
    template_name = "mailing/all_attempts_list.html"
    context_object_name = "attempts"
    paginate_by = 30
    ordering = ["-attempt_datetime"]

    def get_queryset(self):
        return super().get_queryset().select_related('mailing', 'recipient', 'owner')

class UserListView(PermissionRequiredMixin, ListView):
    permission_required = 'auth.view_user'
    model = User
    template_name = "mailing/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    ordering = ["username"]

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
