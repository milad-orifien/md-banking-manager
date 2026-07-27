import logging
from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from psycopg2.errors import UniqueViolation

from repositories.banking_repository import BankingRepository
from repositories.category_repository import CategoryRepository
from routes.decorators import login_required
from services.banking_service import BankingService
from services.excel_service import ExcelService
from services.report_service import ReportService
from services.validation_service import ValidationService

LOGGER = logging.getLogger(__name__)

banking_bp = Blueprint("banking", __name__)
banking_service = BankingService()
category_repository = CategoryRepository()
banking_repository = BankingRepository()
report_service = ReportService()
excel_service = ExcelService()


@banking_bp.route("/dashboard")
@login_required
def dashboard():
    accounts, latest_entries = banking_service.get_dashboard(session["kundenid"])
    if not accounts:
        flash("Legen Sie zuerst ein Finanzkonto an, um den MD Banking Manager zu nutzen.", "info")
        return redirect(url_for("banking.create_account"))
    return render_template(
        "dashboard.html", accounts=accounts, latest_entries=latest_entries
    )


@banking_bp.route("/konten/neu", methods=["GET", "POST"])
@login_required
def create_account():
    if request.method == "POST":
        try:
            account_id = banking_service.create_account(
                session["kundenid"], request.form.get("kontoname")
            )
            flash("Das Finanzkonto wurde angelegt.", "success")
            return redirect(url_for("banking.account_detail", account_id=account_id))
        except UniqueViolation:
            flash("Ein Finanzkonto mit diesem Namen ist bereits vorhanden.", "danger")
        except ValueError as error:
            flash(str(error), "danger")
        except Exception:
            LOGGER.exception("Finanzkonto konnte nicht angelegt werden")
            flash("Das Finanzkonto konnte nicht angelegt werden.", "danger")
    return render_template("account_create.html")


@banking_bp.route("/konto/<int:account_id>")
@login_required
def account_detail(account_id):
    try:
        view_data = banking_service.get_account_view(
            session["kundenid"], account_id, request.args
        )
        categories = category_repository.list_for_user(session["kundenid"])

        sort_urls = {}
        for key in banking_repository.SORT_COLUMNS:
            next_direction = (
                "asc"
                if view_data["sort_key"] == key and view_data["direction"] == "desc"
                else "desc"
            )
            params = request.args.to_dict()
            params.update({"sort": key, "richtung": next_direction})
            sort_urls[key] = url_for(
                "banking.account_detail", account_id=account_id, **params
            )

        more_url = None
        if view_data["has_more"]:
            params = request.args.to_dict()
            params.pop("alle", None)
            params["limit"] = view_data["limit"] + 15
            more_url = url_for(
                "banking.account_detail", account_id=account_id, **params
            )

        all_params = request.args.to_dict()
        all_params.pop("limit", None)
        all_params["alle"] = 1
        all_url = url_for("banking.account_detail", account_id=account_id, **all_params)

        return render_template(
            "account_detail.html",
            categories=categories,
            today=date.today().isoformat(),
            sort_urls=sort_urls,
            more_url=more_url,
            all_url=all_url,
            **view_data,
        )
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
        return redirect(url_for("banking.dashboard"))


@banking_bp.route("/konto/<int:account_id>/bearbeiten", methods=["POST"])
@login_required
def update_account(account_id):
    try:
        new_name = banking_service.update_account_name(
            session["kundenid"], account_id, request.form.get("kontoname")
        )
        flash(f'Das Finanzkonto heißt jetzt „{new_name}“.', "success")
    except UniqueViolation:
        flash("Ein Finanzkonto mit diesem Namen ist bereits vorhanden.", "danger")
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
    except Exception:
        LOGGER.exception("Finanzkonto konnte nicht umbenannt werden")
        flash("Das Finanzkonto konnte nicht umbenannt werden.", "danger")
    return redirect(url_for("banking.account_detail", account_id=account_id))


@banking_bp.route("/konto/<int:account_id>/loeschen", methods=["POST"])
@login_required
def delete_account(account_id):
    try:
        deleted = banking_service.delete_account(
            session["kundenid"], account_id, request.form.get("kontoname_bestaetigung")
        )
        count = int(deleted["anzahl_eintraege"])
        if count == 0:
            message = f'Das Finanzkonto „{deleted["kontoname"]}“ wurde gelöscht.'
        elif count == 1:
            message = (
                f'Das Finanzkonto „{deleted["kontoname"]}“ und eine zugehörige '
                "Buchung wurden gelöscht."
            )
        else:
            message = (
                f'Das Finanzkonto „{deleted["kontoname"]}“ und {count} zugehörige '
                "Buchungen wurden gelöscht."
            )
        flash(message, "success")
        return redirect(url_for("banking.dashboard"))
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
        return redirect(url_for("banking.account_detail", account_id=account_id))
    except Exception:
        LOGGER.exception("Finanzkonto konnte nicht gelöscht werden")
        flash("Das Finanzkonto konnte nicht gelöscht werden.", "danger")
        return redirect(url_for("banking.account_detail", account_id=account_id))


@banking_bp.route("/konto/<int:account_id>/eintrag", methods=["POST"])
@login_required
def create_entry(account_id):
    try:
        banking_service.create_entry(session["kundenid"], account_id, request.form)
        flash("Die Buchung wurde gespeichert.", "success")
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
    except Exception:
        LOGGER.exception("Buchung konnte nicht gespeichert werden")
        flash("Die Buchung konnte nicht gespeichert werden.", "danger")
    return redirect(url_for("banking.account_detail", account_id=account_id))


@banking_bp.route("/eintrag/<int:entry_id>/kategorie", methods=["POST"])
@login_required
def change_entry_category(entry_id):
    try:
        category_id = int(request.form.get("kategorieid", ""))
        account_id = int(request.form.get("kontoid", ""))
        banking_service.change_category(session["kundenid"], entry_id, category_id)
        flash("Die Kategorie wurde geändert.", "success")
        return redirect(url_for("banking.account_detail", account_id=account_id))
    except (ValueError, PermissionError):
        flash("Die Kategorie konnte nicht geändert werden.", "danger")
        return redirect(url_for("banking.dashboard"))


@banking_bp.route("/kategorien")
@login_required
def categories():
    all_categories = category_repository.list_for_user(session["kundenid"])
    manageable_categories = [
        category
        for category in all_categories
        if category["bezeichnung"] != "Nicht kategorisiert"
    ]
    categories_with_keywords = [
        category for category in manageable_categories if category["schlagwoerter"]
    ]
    empty_categories = [
        category for category in manageable_categories if not category["schlagwoerter"]
    ]
    return render_template(
        "categories.html",
        manageable_categories=manageable_categories,
        categories_with_keywords=categories_with_keywords,
        empty_categories=empty_categories,
    )


@banking_bp.route("/kategorien/neu", methods=["POST"])
@login_required
def add_category():
    try:
        name = ValidationService.clean_text(request.form.get("bezeichnung"), 80)
        if not name:
            raise ValueError("Bitte eine Bezeichnung eingeben.")
        category_repository.create(session["kundenid"], name)
        flash("Die Kategorie wurde angelegt.", "success")
    except UniqueViolation:
        flash("Diese Kategorie ist bereits vorhanden.", "danger")
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("banking.categories"))


@banking_bp.route("/schlagwoerter/neu", methods=["POST"])
@login_required
def add_keyword():
    try:
        category_id = int(request.form.get("kategorieid", ""))
        if not category_repository.belongs_to_user(category_id, session["kundenid"]):
            raise PermissionError
        word = ValidationService.clean_text(request.form.get("wort"), 100)
        if not word:
            raise ValueError("Bitte ein Schlagwort eingeben.")
        category_repository.add_keyword(category_id, word)
        flash("Das Schlagwort wurde hinzugefügt.", "success")
    except UniqueViolation:
        flash("Dieses Schlagwort ist bereits vorhanden.", "danger")
    except (ValueError, PermissionError):
        flash("Das Schlagwort konnte nicht hinzugefügt werden.", "danger")
    return redirect(url_for("banking.categories"))


@banking_bp.route("/kategorie/<int:category_id>/bearbeiten", methods=["POST"])
@login_required
def update_category(category_id):
    try:
        name = ValidationService.clean_text(request.form.get("bezeichnung"), 80)
        if not name:
            raise ValueError("Bitte eine Bezeichnung eingeben.")
        if not category_repository.update_category(
            category_id, session["kundenid"], name
        ):
            raise PermissionError("Die Kategorie wurde nicht gefunden.")
        flash(f'Die Kategorie heißt jetzt „{name}“.', "success")
    except UniqueViolation:
        flash("Diese Kategorie ist bereits vorhanden.", "danger")
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
    return redirect(url_for("banking.categories"))


@banking_bp.route("/schlagwort/<int:keyword_id>/bearbeiten", methods=["POST"])
@login_required
def update_keyword(keyword_id):
    try:
        word = ValidationService.clean_text(request.form.get("wort"), 100)
        if not word:
            raise ValueError("Bitte ein Schlagwort eingeben.")
        if not category_repository.update_keyword(
            keyword_id, session["kundenid"], word
        ):
            raise PermissionError("Das Schlagwort wurde nicht gefunden.")
        flash(f'Das Schlagwort wurde in „{word}“ geändert.', "success")
    except UniqueViolation:
        flash("Dieses Schlagwort ist bereits vorhanden.", "danger")
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
    return redirect(url_for("banking.categories"))


@banking_bp.route("/schlagwort/<int:keyword_id>/loeschen", methods=["POST"])
@login_required
def delete_keyword(keyword_id):
    if category_repository.delete_keyword(keyword_id, session["kundenid"]):
        flash("Das Schlagwort wurde gelöscht.", "success")
    else:
        flash("Das Schlagwort wurde nicht gefunden.", "danger")
    return redirect(url_for("banking.categories"))


@banking_bp.route("/kategorie/<int:category_id>/loeschen", methods=["POST"])
@login_required
def delete_category(category_id):
    try:
        deleted = category_repository.delete_category(category_id, session["kundenid"])
        if deleted is None:
            raise PermissionError("Die Kategorie wurde nicht gefunden.")
        count = int(deleted["anzahl_buchungen"])
        if count:
            suffix = "Buchung wird" if count == 1 else "Buchungen werden"
            flash(
                f'Die Kategorie „{deleted["bezeichnung"]}“ wurde gelöscht. '
                f'{count} {suffix} jetzt als „Ohne Kategorie“ geführt.',
                "success",
            )
        else:
            flash(f'Die Kategorie „{deleted["bezeichnung"]}“ wurde gelöscht.', "success")
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
    except Exception:
        LOGGER.exception("Kategorie konnte nicht gelöscht werden")
        flash("Die Kategorie konnte nicht gelöscht werden.", "danger")
    return redirect(url_for("banking.categories"))


@banking_bp.route("/auswertung")
@login_required
def report():
    try:
        report_data = report_service.create_report(session["kundenid"], request.args)
    except (ValueError, PermissionError) as error:
        flash(str(error), "danger")
        report_data = report_service.create_report(session["kundenid"], {})
    accounts = banking_repository.list_accounts(session["kundenid"])
    return render_template("report.html", accounts=accounts, **report_data)


@banking_bp.route("/konto/<int:account_id>/export")
@login_required
def export_account(account_id):
    try:
        file_data, filename = excel_service.export_account(session["kundenid"], account_id)
        return send_file(
            file_data,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except PermissionError as error:
        flash(str(error), "danger")
        return redirect(url_for("banking.dashboard"))


@banking_bp.route("/konto/<int:account_id>/import", methods=["GET", "POST"])
@login_required
def import_account(account_id):
    if not banking_repository.account_belongs_to_user(account_id, session["kundenid"]):
        flash("Auf dieses Finanzkonto besteht kein Zugriff.", "danger")
        return redirect(url_for("banking.dashboard"))

    account = banking_repository.get_account(account_id, session["kundenid"])
    if request.method == "POST":
        try:
            imported, skipped = excel_service.import_account(
                session["kundenid"], account_id, request.files.get("datei")
            )
            message = f"{imported} Buchungen wurden importiert."
            if skipped:
                message += " Übersprungene Zeilen: " + ", ".join(map(str, skipped))
            flash(message, "success" if imported else "warning")
            return redirect(url_for("banking.account_detail", account_id=account_id))
        except (ValueError, PermissionError) as error:
            flash(str(error), "danger")
        except Exception:
            LOGGER.exception("Excel-Import fehlgeschlagen")
            flash("Die Datei konnte nicht importiert werden.", "danger")
    return render_template("import.html", account=account)
