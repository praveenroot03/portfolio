from __future__ import annotations

from urllib.parse import quote

from django.conf import settings
from django.db import models
from django.utils import timezone

from .totp import generate_base32_secret, verify_totp


class UserMFA(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mfa_config",
    )
    secret = models.CharField(max_length=64, default=generate_base32_secret)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    last_verified = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Multi-factor authentication"
        verbose_name_plural = "Multi-factor authentications"

    def __str__(self) -> str:
        return f"MFA configuration for {self.user}" if self.user_id else "Unassigned MFA configuration"

    def build_provisioning_uri(self) -> str:
        username = self.user.get_username()
        issuer = getattr(settings, "MFA_ISSUER_NAME", "Portfolio Admin")
        label = quote(f"{issuer}:{username}")
        issuer_param = quote(issuer)
        secret = quote(self.secret)
        return f"otpauth://totp/{label}?secret={secret}&issuer={issuer_param}"

    def verify_token(self, token: str, valid_window: int = 1) -> bool:
        if not token:
            return False

        if verify_totp(self.secret, token, valid_window=valid_window):
            self.last_verified = timezone.now()
            self.save(update_fields=["last_verified"])
            return True
        return False
