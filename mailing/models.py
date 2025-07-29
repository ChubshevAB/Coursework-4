from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()  # Получаем модель пользователя

class Recipient(models.Model):
    email = models.EmailField(
        max_length=100,
        verbose_name="Email",
        help_text="Введите адрес электронной почты",
    )
    full_name = models.CharField(
        max_length=100, verbose_name="Ф.И.О.", help_text="Укажите фамилию и имя"
    )
    comment = models.TextField(
        max_length=200,
        verbose_name="Коментарий",
        help_text="Напишите комментарий",
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name="Владелец",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["email", "full_name"]
        permissions = [
            ("view_all_recipients", "Может просматривать всех получателей"),
            ("block_recipient", "Может блокировать получателей"),
        ]

    def __str__(self):
        return f"{self.full_name}, {self.email}"


class Message(models.Model):
    title = models.CharField(
        max_length=100, verbose_name="Тема", help_text="Укажите тему сообщения"
    )
    letter = models.TextField(
        max_length=500, verbose_name="Содержание", help_text="Введите текст"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Владелец",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("view_all_messages", "Может просматривать все сообщения"),
            ("disable_message", "Может отключать сообщения"),
        ]

    def __str__(self):
        return self.title


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("completed", "Завершена"),
        ("created", "Создана"),
        ("started", "Запущена"),
    ]

    first_datetime = models.DateTimeField(verbose_name="Дата и время первой отправки")
    end_datetime = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Recipient, related_name="mailings", verbose_name="Получатели"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name="Владелец",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-first_datetime"]
        permissions = [
            ("view_all_mailings", "Может просматривать все рассылки"),
            ("disable_mailing", "Может отключать рассылки"),
            ("view_mailing_stats", "Может просматривать статистику рассылок"),
        ]

    def __str__(self):
        return f"Рассылка {self.id} ({self.get_status_display()})"


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    attempt_datetime = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=7,
        choices=STATUS_CHOICES,
        verbose_name="Статус попытки"
    )
    server_response = models.TextField(
        verbose_name="Ответ почтового сервера",
        blank=True,
        null=True
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка"
    )
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Получатель"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Владелец",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ["-attempt_datetime"]
        permissions = [
            ("view_all_attempts", "Может просматривать все попытки рассылок"),
        ]

    def __str__(self):
        return f"Попытка {self.id} ({self.get_status_display()})"