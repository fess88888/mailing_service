from django.urls import path
from django.views.decorators.cache import cache_page
from .views import (
    HomeView,
    RecipientListView, RecipientDetailView, RecipientCreateView,
    RecipientUpdateView, RecipientDeleteView,
    MessageListView, MessageDetailView, MessageCreateView,
    MessageUpdateView, MessageDeleteView,
    MailingListView, MailingDetailView, MailingCreateView,
    MailingUpdateView, MailingDeleteView,
    send_mailing_view, toggle_mailing_disable,
    StatisticsView, AttemptListView,
)

app_name = "mailing"

urlpatterns = [
    # Главная (кешируется на 60 секунд — серверное кеширование)
    path("", cache_page(60)(HomeView.as_view()), name="home"),

    # Получатели
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path("recipients/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipients/<int:pk>/edit/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipients/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_delete"),

    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),

    # Рассылки
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailings/<int:pk>/send/", send_mailing_view, name="mailing_send"),
    path("mailings/<int:pk>/toggle-disable/", toggle_mailing_disable, name="mailing_toggle_disable"),

    # Попытки
    path("attempts/", AttemptListView.as_view(), name="attempt_list"),

    # Статистика
    path("statistics/", StatisticsView.as_view(), name="statistics"),
]
