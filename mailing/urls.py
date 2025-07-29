from django.urls import path
from .views import home_view
from .views import (
    RecipientListView,
    RecipientDetailView,
    RecipientCreateView,
    RecipientUpdateView,
    RecipientDeleteView,
    MessageListView,
    MessageDetailView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    MailingListView,
    MailingDetailView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
    MailingAttemptListView,
    start_mailing,
    StartMailingView,
    AllMailingsListView,
    AllMessagesListView,
    AllRecipientsListView,
    AllAttemptsListView,
    UserListView,
)
from django.contrib.auth.mixins import PermissionRequiredMixin

urlpatterns = [
    path("", home_view, name="home"),
    # Recipient URLs
    path("recipients/", RecipientListView.as_view(), name="recipient-list"),
    path(
        "recipients/<int:pk>/", RecipientDetailView.as_view(), name="recipient-detail"
    ),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient-create"),
    path(
        "recipients/<int:pk>/update/",
        RecipientUpdateView.as_view(),
        name="recipient-update",
    ),
    path(
        "recipients/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient-delete",
    ),
    # Message URLs
    path("messages/", MessageListView.as_view(), name="message-list"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message-detail"),
    path("messages/create/", MessageCreateView.as_view(), name="message-create"),
    path(
        "messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message-update"
    ),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message-delete"
    ),
    # Mailing URLs
    path("mailings/", MailingListView.as_view(), name="mailing-list"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing-detail"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing-create"),
    path(
        "mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing-update"
    ),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing-delete"
    ),
    # MailingAttempt
    path("attempts/", MailingAttemptListView.as_view(), name="attempt-list"),
    path("mailings/<int:mailing_id>/start/", start_mailing, name="start-mailing"),
    path("mailing/<int:pk>/start/", StartMailingView.as_view(), name="start-mailing"),
    # Moderator URLs
    path(
        "moderator/mailings/", AllMailingsListView.as_view(), name="all-mailings-list"
    ),
    path(
        "moderator/messages/", AllMessagesListView.as_view(), name="all-messages-list"
    ),
    path(
        "moderator/recipients/",
        AllRecipientsListView.as_view(),
        name="all-recipients-list",
    ),
    path(
        "moderator/attempts/", AllAttemptsListView.as_view(), name="all-attempts-list"
    ),
    path("moderator/users/", UserListView.as_view(), name="user-list"),
]
