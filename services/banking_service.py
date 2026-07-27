from datetime import datetime
from decimal import Decimal

from repositories.banking_repository import BankingRepository
from repositories.category_repository import CategoryRepository
from services.validation_service import ValidationService


class BankingService:
    """Verarbeitet Finanzkonten und Buchungen."""
    def __init__(self, banking_repository=None, category_repository=None):
        self.banking = banking_repository or BankingRepository()
        self.categories = category_repository or CategoryRepository()

    def create_account(self, customer_id, name):
        name = ValidationService.clean_text(name, 100)
        if not name:
            raise ValueError("Bitte einen Namen für das Finanzkonto eingeben.")
        return self.banking.create_account(customer_id, name)


    def update_account_name(self, customer_id, account_id, name):
        name = ValidationService.clean_text(name, 100)
        if not name:
            raise ValueError("Bitte einen Namen für das Finanzkonto eingeben.")
        if not self.banking.update_account_name(account_id, customer_id, name):
            raise PermissionError("Auf dieses Finanzkonto besteht kein Zugriff.")
        return name

    def get_dashboard(self, customer_id):
        accounts = self.banking.list_accounts(customer_id)
        latest_entries = self.banking.list_latest_entries(customer_id, limit=5)
        return accounts, latest_entries

    def delete_account(self, customer_id, account_id, confirmation_name):
        account = self.banking.get_account(account_id, customer_id)
        if account is None:
            raise PermissionError("Auf dieses Finanzkonto besteht kein Zugriff.")

        confirmation_name = ValidationService.clean_text(confirmation_name, 100)
        if confirmation_name != account["kontoname"]:
            raise ValueError(
                "Bitte den Namen des Finanzkontos zur Bestätigung genau eingeben."
            )

        deleted = self.banking.delete_account(account_id, customer_id)
        if deleted is None:
            raise PermissionError("Das Finanzkonto konnte nicht gelöscht werden.")
        return deleted

    def create_entry(self, customer_id, account_id, form):
        if not self.banking.account_belongs_to_user(account_id, customer_id):
            raise PermissionError("Auf dieses Finanzkonto besteht kein Zugriff.")

        amount = ValidationService.parse_amount(form.get("betrag"))
        recipient = ValidationService.clean_text(form.get("empfaenger"), 200)
        purpose = ValidationService.clean_text(form.get("verwendungszweck"), 1000)
        timing_mode = (form.get("zeitpunkt") or "").strip()
        if timing_mode == "eigen":
            value_date = ValidationService.parse_custom_datetime(
                form.get("wertstellungsdatum"), form.get("wertstellungszeit")
            )
        elif timing_mode in ("jetzt", ""):
            value_date = datetime.now().replace(second=0, microsecond=0)
        else:
            raise ValueError("Bitte einen gültigen Wertstellungszeitpunkt auswählen.")

        if not recipient or not purpose:
            raise ValueError("Empfänger und Verwendungszweck sind Pflichtfelder.")

        selected_category = form.get("kategorieid")
        category_id = None
        if selected_category:
            try:
                selected_category = int(selected_category)
            except ValueError:
                raise ValueError("Die ausgewählte Kategorie ist ungültig.") from None
            if not self.categories.belongs_to_user(selected_category, customer_id):
                raise PermissionError("Die ausgewählte Kategorie gehört nicht zu diesem Nutzerkonto.")
            category_id = selected_category

        if category_id is None:
            automatic_match = self.categories.find_matching_category(
                customer_id, recipient, purpose
            )
            if automatic_match:
                category_id = automatic_match["kategorieid"]
        if category_id is None:
            category_id = self.categories.get_uncategorized_id(customer_id)

        return self.banking.create_entry(
            account_id=account_id,
            category_id=category_id,
            value_date=value_date,
            amount=amount,
            recipient=recipient,
            purpose=purpose,
        )

    def get_account_view(self, customer_id, account_id, args):
        if not self.banking.account_belongs_to_user(account_id, customer_id):
            raise PermissionError("Auf dieses Finanzkonto besteht kein Zugriff.")

        filters = {
            "purpose": ValidationService.clean_text(args.get("verwendungszweck"), 200),
            "recipient": ValidationService.clean_text(args.get("empfaenger"), 200),
            "date_from": ValidationService.parse_date(args.get("von")),
            "date_to": ValidationService.parse_date(args.get("bis")),
            "amount_min": ValidationService.parse_amount(args.get("betrag_von"), required=False),
            "amount_max": ValidationService.parse_amount(args.get("betrag_bis"), required=False),
        }
        if filters["date_from"] and filters["date_to"] and filters["date_from"] > filters["date_to"]:
            raise ValueError("Das Startdatum darf nicht nach dem Enddatum liegen.")
        if (
            filters["amount_min"] is not None
            and filters["amount_max"] is not None
            and filters["amount_min"] > filters["amount_max"]
        ):
            raise ValueError("Der Mindestbetrag darf nicht größer als der Höchstbetrag sein.")

        sort_key = args.get("sort", "datum")
        if sort_key not in self.banking.SORT_COLUMNS:
            sort_key = "datum"
        direction = "asc" if args.get("richtung") == "asc" else "desc"

        show_all = args.get("alle") == "1"
        if show_all:
            limit = None
        else:
            try:
                limit = int(args.get("limit", 15))
            except (TypeError, ValueError):
                limit = 15
            limit = min(max(limit, 15), 300)

        account = self.banking.get_account(account_id, customer_id)
        entries = self.banking.list_entries(
            account_id=account_id,
            filters=filters,
            sort_key=sort_key,
            direction=direction,
            limit=limit,
        )
        summary = self.banking.count_and_sum_entries(account_id, filters)
        has_more = limit is not None and summary["anzahl"] > limit

        return {
            "account": account,
            "entries": entries,
            "filters": filters,
            "sort_key": sort_key,
            "direction": direction,
            "limit": limit,
            "show_all": show_all,
            "has_more": has_more,
            "summary": summary,
        }

    def change_category(self, customer_id, entry_id, category_id):
        if not self.categories.belongs_to_user(category_id, customer_id):
            raise PermissionError("Die Kategorie gehört nicht zu diesem Nutzerkonto.")
        if not self.banking.update_entry_category(entry_id, category_id, customer_id):
            raise PermissionError("Die Buchung konnte nicht geändert werden.")

    @staticmethod
    def calculate_percentages(rows):
        total = sum((row["summe"] for row in rows), Decimal("0"))
        result = []
        for row in rows:
            percentage = Decimal("0") if total == 0 else (row["summe"] / total * 100)
            result.append(
                {
                    "kategorie": row["kategorie"],
                    "summe": row["summe"],
                    "anteil": percentage.quantize(Decimal("0.1")),
                }
            )
        return result, total
