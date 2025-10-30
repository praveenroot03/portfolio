from django.contrib import admin
from django.utils.html import format_html

from .models import UserMFA


@admin.register(UserMFA)
class UserMFAAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "last_verified", "updated")
    list_filter = ("is_active", "updated")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created", "updated", "last_verified", "provisioning_uri_display")
    fields = (
        "user",
        "is_active",
        "secret",
        "provisioning_uri_display",
        "last_verified",
        "created",
        "updated",
    )

    def provisioning_uri_display(self, instance):
        if not instance.secret:
            return ""
        uri = instance.build_provisioning_uri()
        return format_html("<code>{}</code>", uri)

    provisioning_uri_display.short_description = "Provisioning URI"
