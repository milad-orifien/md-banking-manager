from werkzeug.security import check_password_hash, generate_password_hash

from config import Config


class SecurityService:
    """Erstellt und prüft Passwort-Hashes."""

    @staticmethod
    def ensure_hash_method_available():
        if not Config.HASH_METHOD.startswith(("pbkdf2:sha256", "pbkdf2:sha512")):
            raise RuntimeError(
                "Das konfigurierte Hash-Verfahren ist nicht freigegeben. "
                "Verwenden Sie PBKDF2 mit SHA-256 oder SHA-512."
            )

    @classmethod
    def hash_password(cls, password):
        cls.ensure_hash_method_available()
        return generate_password_hash(password, method=Config.HASH_METHOD)

    @staticmethod
    def verify_password(password_hash, password):
        return check_password_hash(password_hash, password)
