from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time
from typing import Optional


def _normalize_base32(secret: str) -> bytes:
    secret = secret.strip().replace(" ", "").upper()
    missing_padding = (-len(secret)) % 8
    if missing_padding:
        secret += "=" * missing_padding
    return base64.b32decode(secret, casefold=True)


def generate_base32_secret(length: int = 32) -> str:
    raw = secrets.token_bytes(length)
    encoded = base64.b32encode(raw).decode("utf-8")
    return encoded.strip("=")


def _totp_counter(timestamp: Optional[float] = None, *, time_step: int = 30) -> int:
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp // time_step)


def totp_at(secret: str, timestamp: Optional[float] = None, *, digits: int = 6, time_step: int = 30) -> str:
    key = _normalize_base32(secret)
    counter = _totp_counter(timestamp, time_step=time_step)
    counter_bytes = struct.pack(">Q", counter)
    digest = hmac.new(key, counter_bytes, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    truncated = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    token = truncated % (10 ** digits)
    return str(token).zfill(digits)


def verify_totp(secret: str, token: str, *, valid_window: int = 1, digits: int = 6, time_step: int = 30) -> bool:
    if not token:
        return False

    token = token.strip().replace(" ", "")
    if not token.isdigit():
        return False

    current_counter = _totp_counter(time_step=time_step)
    for offset in range(-valid_window, valid_window + 1):
        counter_time = (current_counter + offset) * time_step
        if totp_at(secret, counter_time, digits=digits, time_step=time_step) == token:
            return True
    return False
