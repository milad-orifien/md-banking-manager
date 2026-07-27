from calendar import monthrange
from datetime import date

from repositories.banking_repository import BankingRepository
from services.banking_service import BankingService
from services.validation_service import ValidationService


class ReportService:
    """Erstellt die Daten für die Auswertungsseite."""
    def __init__(self, banking_repository=None):
        self.banking = banking_repository or BankingRepository()

    def create_report(self, customer_id, args):
        period = args.get("zeitraum", "gesamt")
        date_from = None
        date_to = None

        if period == "monat":
            month_value = (args.get("monat") or "").strip()
            try:
                year, month = [int(part) for part in month_value.split("-")]
                date_from = date(year, month, 1)
                date_to = date(year, month, monthrange(year, month)[1])
            except (ValueError, TypeError):
                raise ValueError("Bitte einen gültigen Monat auswählen.") from None
        elif period == "jahr":
            try:
                year = int(args.get("jahr"))
                date_from = date(year, 1, 1)
                date_to = date(year, 12, 31)
            except (ValueError, TypeError):
                raise ValueError("Bitte ein gültiges Jahr eingeben.") from None
        elif period == "benutzerdefiniert":
            date_from = ValidationService.parse_date(args.get("von"))
            date_to = ValidationService.parse_date(args.get("bis"))
            if not date_from or not date_to:
                raise ValueError("Für den freien Zeitraum werden ein Start- und Enddatum benötigt.")
            if date_from > date_to:
                raise ValueError("Das Startdatum darf nicht nach dem Enddatum liegen.")
        elif period != "gesamt":
            period = "gesamt"

        account_id = args.get("kontoid")
        if account_id:
            try:
                account_id = int(account_id)
            except ValueError:
                account_id = None
            if account_id and not self.banking.account_belongs_to_user(account_id, customer_id):
                raise PermissionError("Auf dieses Finanzkonto besteht kein Zugriff.")

        rows = self.banking.report_expenses(customer_id, date_from, date_to, account_id)
        report, total = BankingService.calculate_percentages(rows)
        return {
            "period": period,
            "date_from": date_from,
            "date_to": date_to,
            "account_id": account_id,
            "rows": report,
            "total": total,
        }
