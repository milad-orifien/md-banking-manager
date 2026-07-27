import secrets

from repositories.banking_repository import BankingRepository
from repositories.community_repository import CommunityRepository
from repositories.user_repository import UserRepository
from services.banking_service import BankingService
from services.validation_service import ValidationService


class CommunityService:
    """Verarbeitet Gruppen, Einladungen und Nachrichten."""
    def __init__(
        self,
        community_repository=None,
        user_repository=None,
        banking_repository=None,
    ):
        self.community = community_repository or CommunityRepository()
        self.users = user_repository or UserRepository()
        self.banking = banking_repository or BankingRepository()

    def create_group(self, customer_id, name):
        name = ValidationService.clean_text(name, 100)
        if not name:
            raise ValueError("Bitte einen Gruppennamen eingeben.")
        return self.community.create_group(customer_id, name)

    def invite(self, group_id, sender_id, recipient_email, invitation_url_builder):
        group = self.community.get_group(group_id, sender_id)
        if not group:
            raise PermissionError("Auf diese Gruppe besteht kein Zugriff.")
        recipient = self.users.find_by_email(recipient_email)
        if not recipient:
            raise ValueError("Unter dieser E-Mail-Adresse ist kein Nutzer registriert.")
        if recipient["kundenid"] == sender_id:
            raise ValueError("Eine Einladung an das eigene Nutzerkonto ist nicht möglich.")
        if self.community.is_member(group_id, recipient["kundenid"]):
            raise ValueError("Diese Person ist bereits Mitglied der Gruppe.")

        token = secrets.token_urlsafe(32)
        invitation_id = self.community.create_invitation(
            group_id, sender_id, recipient["kundenid"], token
        )
        invitation_url = invitation_url_builder(token)
        content = (
            f"Sie wurden in die Gruppe „{group['gruppenname']}“ eingeladen. "
            f"Über diesen Link können Sie beitreten: {invitation_url}"
        )
        self.community.send_message(
            sender_id,
            recipient["kundenid"],
            f"Einladung: {group['gruppenname']}",
            content,
            invitation_id,
        )

    def accept_invitation(self, token, customer_id):
        invitation = self.community.get_invitation(token)
        if not invitation:
            raise ValueError("Die Einladung wurde nicht gefunden.")
        if invitation["empfaengerid"] != customer_id:
            raise PermissionError("Diese Einladung ist für ein anderes Nutzerkonto bestimmt.")
        if invitation["angenommen"] or self.community.is_member(invitation["gruppenid"], customer_id):
            return invitation["gruppenid"], False
        self.community.accept_invitation(
            invitation["einladungid"], invitation["gruppenid"], customer_id
        )
        return invitation["gruppenid"], True

    def send_private_message(self, sender_id, recipient_email, subject, content):
        recipient = self.users.find_by_email(recipient_email)
        if not recipient:
            raise ValueError("Unter dieser E-Mail-Adresse ist kein Nutzer registriert.")
        if recipient["kundenid"] == sender_id:
            raise ValueError("Eine Nachricht an das eigene Nutzerkonto ist nicht möglich.")
        subject = ValidationService.clean_text(subject, 150)
        content = ValidationService.clean_text(content, 3000)
        if not subject or not content:
            raise ValueError("Betreff und Nachrichtentext sind Pflichtfelder.")
        return self.community.send_message(
            sender_id, recipient["kundenid"], subject, content
        )

    def get_shared_member(self, viewer_id, owner_id, group_id):
        if not self.community.users_share_group(viewer_id, owner_id, group_id):
            raise PermissionError("Die Finanzkontoansicht ist nur innerhalb derselben Gruppe möglich.")
        owner = self.users.find_by_id(owner_id)
        accounts = self.banking.list_accounts(owner_id)
        report_rows = self.banking.report_expenses(owner_id)
        report, total = BankingService.calculate_percentages(report_rows)
        return owner, accounts, report, total

    def get_shared_account(self, viewer_id, owner_id, group_id, account_id):
        if not self.community.users_share_group(viewer_id, owner_id, group_id):
            raise PermissionError("Die Finanzkontoansicht ist nur innerhalb derselben Gruppe möglich.")
        account = self.banking.get_account(account_id, owner_id)
        if not account:
            raise PermissionError("Das Finanzkonto gehört nicht zum ausgewählten Gruppenmitglied.")
        entries = self.banking.list_entries(
            account_id=account_id,
            filters={},
            sort_key="datum",
            direction="desc",
            limit=None,
        )
        owner = self.users.find_by_id(owner_id)
        return owner, account, entries
