import secrets

from flask import session


class CsrfService:
    """Prüft den CSRF-Token bei Formularen."""

    SESSION_KEY = "csrf_token"

    @classmethod
    def get_token(cls):
        token = session.get(cls.SESSION_KEY)
        if not token:
            token = secrets.token_urlsafe(32)
            session[cls.SESSION_KEY] = token
        return token

    @classmethod
    def is_valid(cls, submitted_token):
        stored_token = session.get(cls.SESSION_KEY)
        return bool(
            stored_token
            and submitted_token
            and secrets.compare_digest(stored_token, submitted_token)
        )
