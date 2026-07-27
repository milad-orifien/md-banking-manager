import logging

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from repositories.user_repository import UserRepository
from routes.decorators import login_required
from services.auth_service import AuthService

LOGGER = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()
user_repository = UserRepository()


def _start_session(user):
    session.clear()
    session["kundenid"] = user["kundenid"]
    session["vorname"] = user["vorname"]


@auth_bp.route("/registrieren", methods=["GET", "POST"])
def register():
    if session.get("kundenid"):
        return redirect(url_for("banking.dashboard"))

    if request.method == "POST":
        try:
            pending_invite = session.get("pending_invite")
            user = auth_service.register(request.form)
            _start_session(user)
            flash(
                f"Willkommen, {user['vorname']}! Die Registrierung war erfolgreich.",
                "success",
            )
            if pending_invite:
                return redirect(
                    url_for("community.accept_invitation", token=pending_invite)
                )
            return redirect(url_for("banking.dashboard"))
        except ValueError as error:
            flash(str(error), "danger")
        except Exception:
            LOGGER.exception("Registrierung fehlgeschlagen")
            flash(
                "Die Registrierung konnte gerade nicht abgeschlossen werden.",
                "danger",
            )

    return render_template("register.html", form=request.form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("kundenid"):
        return redirect(url_for("banking.dashboard"))

    if request.method == "POST":
        try:
            pending_invite = session.get("pending_invite")
            user = auth_service.login(
                request.form.get("email"), request.form.get("passwort")
            )
            _start_session(user)
            flash(f"Hallo {user['vorname']}, Sie sind jetzt angemeldet.", "success")
            if pending_invite:
                return redirect(
                    url_for("community.accept_invitation", token=pending_invite)
                )
            return redirect(url_for("banking.dashboard"))
        except ValueError as error:
            flash(str(error), "danger")
        except Exception:
            LOGGER.exception("Anmeldung fehlgeschlagen")
            flash("Die Anmeldung konnte gerade nicht durchgeführt werden.", "danger")

    return render_template("login.html", form=request.form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    first_name = session.get("vorname", "")
    session.clear()
    message = (
        f"Auf Wiedersehen, {first_name}!" if first_name else "Sie wurden abgemeldet."
    )
    flash(message, "success")
    return redirect(url_for("index"))


@auth_bp.route("/profil")
@login_required
def profile():
    user = user_repository.find_by_id(session["kundenid"])
    return render_template("profile.html", user=user)


@auth_bp.route("/profil/daten", methods=["POST"])
@login_required
def update_profile():
    try:
        user = auth_service.update_profile(session["kundenid"], request.form)
        session["vorname"] = user["vorname"]
        flash("Die Profildaten wurden gespeichert.", "success")
    except ValueError as error:
        flash(str(error), "danger")
    except Exception:
        LOGGER.exception("Profildaten konnten nicht gespeichert werden")
        flash("Die Profildaten konnten nicht gespeichert werden.", "danger")
    return redirect(url_for("auth.profile"))


@auth_bp.route("/profil/passwort", methods=["POST"])
@login_required
def change_password():
    try:
        auth_service.change_password(session["kundenid"], request.form)
        flash("Das Passwort wurde geändert.", "success")
    except ValueError as error:
        flash(str(error), "danger")
    except Exception:
        LOGGER.exception("Passwort konnte nicht geändert werden")
        flash("Das Passwort konnte nicht geändert werden.", "danger")
    return redirect(url_for("auth.profile"))
