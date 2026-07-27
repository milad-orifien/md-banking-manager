import logging

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from repositories.community_repository import CommunityRepository
from routes.decorators import login_required
from services.community_service import CommunityService

LOGGER = logging.getLogger(__name__)

community_bp = Blueprint("community", __name__)
community_service = CommunityService()
community_repository = CommunityRepository()


@community_bp.route("/gruppen", methods=["GET", "POST"])
@login_required
def groups():
    if request.method == "POST":
        try:
            group_id = community_service.create_group(
                session["kundenid"], request.form.get("gruppenname")
            )
            flash("Die Gruppe wurde erstellt.", "success")
            return redirect(url_for("community.group_detail", group_id=group_id))
        except ValueError as error:
            flash(str(error), "danger")
    groups_for_user = community_repository.list_groups_for_user(session["kundenid"])
    return render_template("groups.html", groups=groups_for_user)


@community_bp.route("/gruppe/<int:group_id>")
@login_required
def group_detail(group_id):
    group = community_repository.get_group(group_id, session["kundenid"])
    if not group:
        flash("Auf diese Gruppe besteht kein Zugriff.", "danger")
        return redirect(url_for("community.groups"))
    members = community_repository.list_group_members(group_id)
    return render_template("group_detail.html", group=group, members=members)


@community_bp.route("/gruppe/<int:group_id>/einladen", methods=["POST"])
@login_required
def invite(group_id):
    try:
        community_service.invite(
            group_id,
            session["kundenid"],
            request.form.get("email"),
            lambda token: url_for(
                "community.accept_invitation", token=token, _external=True
            ),
        )
        flash("Die Einladung wurde als private Nachricht versendet.", "success")
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
    except Exception:
        LOGGER.exception("Einladung konnte nicht versendet werden")
        flash("Die Einladung konnte nicht versendet werden.", "danger")
    return redirect(url_for("community.group_detail", group_id=group_id))


@community_bp.route("/einladung/<token>")
def accept_invitation(token):
    if not session.get("kundenid"):
        session["pending_invite"] = token
        flash("Bitte anmelden, um die Gruppeneinladung anzunehmen.", "info")
        return redirect(url_for("auth.login"))
    try:
        group_id, joined = community_service.accept_invitation(token, session["kundenid"])
        flash(
            "Sie sind der Gruppe beigetreten."
            if joined
            else "Sie sind bereits Mitglied dieser Gruppe.",
            "success" if joined else "info",
        )
        return redirect(url_for("community.group_detail", group_id=group_id))
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
        return redirect(url_for("community.groups"))


@community_bp.route("/nachrichten")
@login_required
def messages():
    inbox = community_repository.list_inbox(session["kundenid"])
    return render_template("messages.html", messages=inbox)


@community_bp.route("/nachrichten/neu", methods=["GET", "POST"])
@login_required
def send_message():
    if request.method == "POST":
        try:
            community_service.send_private_message(
                session["kundenid"],
                request.form.get("email"),
                request.form.get("betreff"),
                request.form.get("inhalt"),
            )
            flash("Die Nachricht wurde versendet.", "success")
            return redirect(url_for("community.messages"))
        except ValueError as error:
            flash(str(error), "danger")
    return render_template("message_create.html", form=request.form)


@community_bp.route("/nachricht/<int:message_id>/gelesen", methods=["POST"])
@login_required
def mark_message_read(message_id):
    community_repository.mark_read(message_id, session["kundenid"])
    return redirect(url_for("community.messages"))


@community_bp.route("/gruppe/<int:group_id>/mitglied/<int:owner_id>")
@login_required
def shared_member(group_id, owner_id):
    try:
        owner, accounts, report_rows, report_total = community_service.get_shared_member(
            session["kundenid"], owner_id, group_id
        )
        return render_template(
            "shared_member.html",
            group_id=group_id,
            owner=owner,
            accounts=accounts,
            report_rows=report_rows,
            report_total=report_total,
        )
    except PermissionError as error:
        flash(str(error), "danger")
        return redirect(url_for("community.groups"))


@community_bp.route(
    "/gruppe/<int:group_id>/mitglied/<int:owner_id>/konto/<int:account_id>"
)
@login_required
def shared_account(group_id, owner_id, account_id):
    try:
        owner, account, entries = community_service.get_shared_account(
            session["kundenid"], owner_id, group_id, account_id
        )
        return render_template(
            "shared_account.html",
            group_id=group_id,
            owner=owner,
            account=account,
            entries=entries,
        )
    except PermissionError as error:
        flash(str(error), "danger")
        return redirect(url_for("community.groups"))
