"""Utility helpers for the main application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from ip2geotools.databases.noncommercial import DbIpCity


@dataclass(frozen=True)
class ClientMeta:
    """A lightweight container describing a visitor."""

    ip_address: str
    user_agent: str


class Utility:
    """Collection of helpers used across the app."""

    def get_client_ip_address(self, request) -> str:
        """Return the visitor IP, accounting for proxied requests."""

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    def get_user_agent(self, request) -> str:
        """Return the raw user agent string for the request."""

        return request.META.get("HTTP_USER_AGENT", "")

    @staticmethod
    def get_location_via_ip(ip_addr: str) -> Optional[Dict[str, str]]:
        """Resolve a location dictionary for the provided IP address."""

        if not ip_addr:
            return None

        try:
            response = DbIpCity.get(str(ip_addr), api_key="free")
        except Exception:  # pragma: no cover - defensive against API errors.
            return None

        return {
            "city": response.city,
            "region": response.region,
            "country": response.country,
        }


# Backwards compatibility with the previous import style.
utlity = Utility

