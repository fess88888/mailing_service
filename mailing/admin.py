from django.contrib import admin
from .models import Recipient, Message, Mailing, Attempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "owner", "created_at")
    list_filter = ("owner",)
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner", "created_at")
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "message", "owner", "is_disabled", "created_at")
    list_filter = ("owner", "is_disabled")
    filter_horizontal = ("recipients",)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("attempt_time", "status", "mailing")
    list_filter = ("status",)
    readonly_fields = ("attempt_time", "status", "server_response", "mailing")
