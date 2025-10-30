from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        from django.contrib import admin

        from .forms import MFAAuthenticationForm

        admin.site.login_form = MFAAuthenticationForm
        admin.site.login_template = "accounts/login.html"
