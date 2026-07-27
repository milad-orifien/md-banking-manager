from repositories.category_repository import CategoryRepository
from repositories.user_repository import UserRepository
from services.security_service import SecurityService
from services.validation_service import ValidationService


class AuthService:
    """Verarbeitet Anmeldung, Registrierung und Profiländerungen."""

    def __init__(self, user_repository=None, category_repository=None):
        self.users = user_repository or UserRepository()
        self.categories = category_repository or CategoryRepository()

    def register(self, form):
        first_name = ValidationService.clean_text(form.get("vorname"), 50)
        last_name = ValidationService.clean_text(form.get("nachname"), 100)
        email = ValidationService.validate_email(form.get("email"))
        age = ValidationService.parse_optional_age(form.get("alter"))
        bank_name = ValidationService.clean_text(form.get("bankinstitut"), 100) or None
        password = form.get("passwort", "")
        password_repeat = form.get("passwort2", "")

        if not first_name or not last_name:
            raise ValueError("Vorname und Nachname sind Pflichtfelder.")
        if password != password_repeat:
            raise ValueError("Die Passwörter stimmen nicht überein.")
        ValidationService.validate_password(password)
        if self.users.email_exists(email):
            raise ValueError("Diese E-Mail-Adresse ist bereits registriert.")

        customer_id = self.users.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=SecurityService.hash_password(password),
            age=age,
            bank_name=bank_name,
        )
        try:
            self.categories.create_default_categories(customer_id)
        except Exception:
            self.users.delete(customer_id)
            raise
        return self.users.find_by_id(customer_id)

    def login(self, email, password):
        email = ValidationService.validate_email(email)
        user = self.users.find_by_email(email)
        if not user or not SecurityService.verify_password(
            user["passwort_hash"], password
        ):
            raise ValueError("E-Mail-Adresse oder Passwort ist falsch.")
        return user

    def update_profile(self, customer_id, form):
        first_name = ValidationService.clean_text(form.get("vorname"), 50)
        last_name = ValidationService.clean_text(form.get("nachname"), 100)
        age = ValidationService.parse_optional_age(form.get("alter"))
        bank_name = ValidationService.clean_text(form.get("bankinstitut"), 100) or None
        if not first_name or not last_name:
            raise ValueError("Vorname und Nachname sind Pflichtfelder.")
        self.users.update_profile(
            customer_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            bank_name=bank_name,
        )
        return self.users.find_by_id(customer_id)

    def change_password(self, customer_id, form):
        current_password = form.get("aktuelles_passwort", "")
        new_password = form.get("neues_passwort", "")
        new_password_repeat = form.get("neues_passwort2", "")

        user = self.users.find_auth_by_id(customer_id)
        if not user or not SecurityService.verify_password(
            user["passwort_hash"], current_password
        ):
            raise ValueError("Das aktuelle Passwort ist falsch.")
        if new_password != new_password_repeat:
            raise ValueError("Die neuen Passwörter stimmen nicht überein.")
        ValidationService.validate_password(new_password)
        if SecurityService.verify_password(user["passwort_hash"], new_password):
            raise ValueError("Das neue Passwort muss sich vom aktuellen Passwort unterscheiden.")

        self.users.update_password_hash(
            customer_id, SecurityService.hash_password(new_password)
        )
