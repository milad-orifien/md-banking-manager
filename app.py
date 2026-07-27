import logging
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, abort, render_template, request

from config import Config
from routes.auth_routes import auth_bp
from routes.banking_routes import banking_bp
from routes.community_routes import community_bp
from services.csrf_service import CsrfService

LOGGER = logging.getLogger(__name__)


def format_euro(value):
    """Formatiert einen Geldbetrag im deutschen Zahlenformat."""
    try:
        amount = Decimal(str(value or 0)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, TypeError):
        amount = Decimal("0.00")
    formatted = f"{amount:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def format_percent(value):
    """Formatiert Prozentwerte mit deutschem Dezimaltrennzeichen."""
    try:
        number = Decimal(str(value or 0)).quantize(Decimal("0.1"))
    except (InvalidOperation, ValueError, TypeError):
        number = Decimal("0.0")
    return f"{number:.1f}".replace(".", ",") + " %"


def format_datetime_de(value):
    if isinstance(value, datetime):
        return value.strftime("%d.%m.%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")
    return value or ""


def display_category(value):
    """Zeigt die technische Auffangkategorie verständlich in der Oberfläche an."""
    return "Ohne Kategorie" if value == "Nicht kategorisiert" else (value or "Ohne Kategorie")


def natural_keyword(value):
    """Verhindert eine unnötige Versalschrift bei vollständig groß geschriebenen Schlagwörtern."""
    text = str(value or "")
    return text.title() if text.isupper() else text


def create_app():
    """Erstellt die Flask-Anwendung und bindet die Routen ein."""

    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "APP_SECRET_KEY fehlt. Bitte eine lokale .env-Datei anhand von "
            ".env.example anlegen."
        )

    app.jinja_env.filters["euro"] = format_euro
    app.jinja_env.filters["prozent"] = format_percent
    app.jinja_env.filters["datum_zeit"] = format_datetime_de
    app.jinja_env.filters["kategorie_anzeige"] = display_category
    app.jinja_env.filters["schlagwort_anzeige"] = natural_keyword

    app.register_blueprint(auth_bp)
    app.register_blueprint(banking_bp)
    app.register_blueprint(community_bp)

    @app.context_processor
    def inject_global_template_values():
        return {"csrf_token": CsrfService.get_token}

    @app.before_request
    def protect_post_requests():
        if request.method == "POST" and not CsrfService.is_valid(
            request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        ):
            abort(400)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/impressum")
    def impressum():
        return render_template("impressum.html")

    @app.route("/datenschutz")
    def datenschutz():
        return render_template("datenschutz.html")

    @app.errorhandler(400)
    def bad_request(_error):
        return render_template(
            "error.html",
            title="Anfrage nicht möglich",
            message="Die Anfrage war nicht gültig. Bitte laden Sie die Seite neu und versuchen Sie es erneut.",
        ), 400

    @app.errorhandler(413)
    def file_too_large(_error):
        return render_template(
            "error.html",
            title="Datei zu groß",
            message="Die hochgeladene Datei darf höchstens 5 MB groß sein.",
        ), 413

    @app.errorhandler(404)
    def page_not_found(_error):
        return render_template(
            "error.html",
            title="Seite nicht gefunden",
            message="Die angeforderte Seite wurde nicht gefunden.",
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        LOGGER.error(
            "Unerwarteter Anwendungsfehler",
            exc_info=(type(error), error, error.__traceback__),
        )
        return render_template(
            "error.html",
            title="Technischer Fehler",
            message="Die Aktion konnte gerade nicht abgeschlossen werden. Bitte versuchen Sie es später erneut.",
        ), 500

    return app


app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("FLASK_PORT", "5001"))
    app.run(
        host="127.0.0.1",
        port=port,
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        use_reloader=False,
    )
