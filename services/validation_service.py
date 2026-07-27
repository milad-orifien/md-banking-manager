import re
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class ValidationService:
    """Prüft Eingaben aus Formularen und Excel-Dateien."""

    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @staticmethod
    def clean_text(value, max_length=None):
        text = (value or "").strip()
        if max_length and len(text) > max_length:
            raise ValueError(f"Die Eingabe darf höchstens {max_length} Zeichen lang sein.")
        return text

    @classmethod
    def validate_email(cls, email):
        email = cls.clean_text(email, 100).lower()
        if not cls.EMAIL_PATTERN.match(email):
            raise ValueError("Bitte eine gültige E-Mail-Adresse eingeben.")
        return email

    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            raise ValueError("Das Passwort muss mindestens acht Zeichen lang sein.")
        if not any(char.isupper() for char in password):
            raise ValueError("Das Passwort muss mindestens einen Großbuchstaben enthalten.")
        if not any(char.islower() for char in password):
            raise ValueError("Das Passwort muss mindestens einen Kleinbuchstaben enthalten.")
        special_positions = [
            index for index, char in enumerate(password) if not char.isalnum()
        ]
        if not special_positions:
            raise ValueError("Das Passwort muss mindestens ein Sonderzeichen enthalten.")
        if 0 in special_positions or len(password) - 1 in special_positions:
            raise ValueError("Das Sonderzeichen darf nicht am Anfang oder Ende stehen.")
        return password

    @staticmethod
    def parse_optional_age(value):
        value = (value or "").strip()
        if not value:
            return None
        if not value.isdigit() or not 1 <= int(value) <= 119:
            raise ValueError("Bitte ein gültiges Alter zwischen 1 und 119 eingeben.")
        return int(value)

    @staticmethod
    def parse_amount(value, *, required=True):
        value = (value or "").strip().replace(",", ".")
        if not value and not required:
            return None
        try:
            amount = Decimal(value).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError):
            raise ValueError("Bitte einen gültigen Betrag eingeben.") from None
        if required and amount == 0:
            raise ValueError("Der Betrag darf nicht 0 sein.")
        return amount

    @staticmethod
    def parse_custom_datetime(date_value, time_value):
        """Verbindet getrennte Datums- und Uhrzeitfelder zu einem Zeitpunkt."""
        date_value = (date_value or "").strip()
        time_value = (time_value or "").strip()
        if not date_value or not time_value:
            raise ValueError("Bitte Datum und Uhrzeit vollständig angeben.")
        try:
            return datetime.strptime(
                f"{date_value} {time_value}", "%Y-%m-%d %H:%M"
            )
        except ValueError:
            raise ValueError("Bitte ein gültiges Datum und eine gültige Uhrzeit eingeben.") from None

    @staticmethod
    def parse_date(value):
        value = (value or "").strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Bitte ein gültiges Datum eingeben.") from None
