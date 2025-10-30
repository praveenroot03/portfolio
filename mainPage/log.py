"""Visitor logging helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Mapping, MutableMapping, Optional

from django.db.models import F
from django.utils import timezone

from mainPage.models import People, Visit_detail


ANONYMOUS_EMAIL = "anonymous@example.com"
ANONYMOUS_NAME = "Visitor"


@dataclass
class Feedback:
    """Normalized structure for feedback submitted through the site."""

    name: str
    email: str
    message: str

    @classmethod
    def from_mapping(cls, payload: Optional[Mapping[str, str]]) -> "Feedback":
        payload = payload or {}
        return cls(
            name=payload.get("name", ANONYMOUS_NAME).strip() or ANONYMOUS_NAME,
            email=payload.get("email", ANONYMOUS_EMAIL).strip() or ANONYMOUS_EMAIL,
            message=payload.get("message", "").strip(),
        )


class VisitorLogger:
    """Persist visitor metadata to the database."""

    cooldown = timedelta(minutes=5)

    def add(self, ip_addr: str, user_agent: str, feedback: Optional[Mapping[str, str]] = None) -> None:
        if not ip_addr:
            return

        feedback_payload = Feedback.from_mapping(feedback)
        person, created = People.objects.get_or_create(
            ip_address=ip_addr,
            defaults={"last_visited": timezone.now()},
        )

        should_increment_visits = (not created) and (
            timezone.now() - person.last_visited >= self.cooldown
        )
        update_kwargs: MutableMapping[str, object] = {"last_visited": timezone.now()}

        if should_increment_visits:
            update_kwargs["no_of_visits"] = F("no_of_visits") + 1

        People.objects.filter(pk=person.pk).update(**update_kwargs)
        person.refresh_from_db()

        Visit_detail.objects.create(
            people=person,
            user_agent=user_agent,
            name=feedback_payload.name,
            email_id=feedback_payload.email,
            message=feedback_payload.message,
        )


# Backwards compatibility with the historic class name.
logger = VisitorLogger

