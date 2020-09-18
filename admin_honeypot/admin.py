from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from admin_honeypot.models import LoginAttempt


class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'password','get_ip_address', 'get_session_key', 'timestamp', 'get_path')
    list_filter = ('timestamp',)
    readonly_fields = ('ip_address', 'username', 'password', 'path', 'session_key', 'user_agent')
    search_fields = ('username', 'ip_address', 'user_agent', 'path')

    def get_actions(self, request):
        actions = super(LoginAttemptAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions



    def get_session_key(self, instance):
        return format_html('<a href="">{sk}</a>', sk=instance.session_key)
    get_session_key.short_description = _('Session')

    def get_ip_address(self, instance):
        return format_html('<a href="https://www.infobyip.com/ip-{ip}.html" target="_blank" >{ip}</a>', ip=instance.ip_address)
    get_ip_address.short_description = _('IP Address')

    def get_path(self, instance):
        return format_html('<a href="">{path}</a>', path=instance.path)
    get_path.short_description = _('URL')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(LoginAttempt, LoginAttemptAdmin)