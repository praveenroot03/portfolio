from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import UserMFA


class MFAAuthenticationForm(AuthenticationForm):
    token = forms.CharField(
        label=_("One-time code"),
        required=False,
        help_text=_("Required if your account has multi-factor authentication enabled."),
        widget=forms.TextInput(attrs={"autocomplete": "one-time-code"}),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        "mfa_required": _("Enter the code from your authenticator app to continue."),
        "invalid_mfa": _("The authentication code you entered is invalid or has expired."),
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        try:
            config = user.mfa_config
        except UserMFA.DoesNotExist:
            return

        if not config.is_active:
            return

        token = self.cleaned_data.get("token", "")
        token = token.replace(" ", "").strip()

        if not token:
            raise forms.ValidationError(self.error_messages["mfa_required"], code="mfa_required")

        if not config.verify_token(token):
            raise forms.ValidationError(self.error_messages["invalid_mfa"], code="invalid_mfa")
