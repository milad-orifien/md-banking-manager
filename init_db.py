from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from database.connection import Database
from services.security_service import SecurityService

BASE_DIR = Path(__file__).resolve().parent


# Demo-Benutzer: E-Mail, Vorname, Nachname, Alter, Bankinstitut, Passwort
DEMO_USERS = [
    ("anna.mueller@example.com", "Anna", "Müller", 28, "Sparkasse", "AnnaTest!123"),
    ("ben.schmidt@example.com", "Ben", "Schmidt", 35, "Volksbank", "BenTest!123"),
    ("clara.weiss@example.com", "Clara", "Weiß", 22, None, "ClaraTest!123"),
]


# Diese Kategorien werden für jeden Demo-Benutzer angelegt.
DEFAULT_CATEGORIES = [
    "Nicht kategorisiert",
    "Einkaufen",
    "Miete",
    "Mobilität",
    "Freizeit",
    "Gehalt",
]


# Die Schlüssel müssen exakt mit den Kategorienamen oben übereinstimmen.
KEYWORDS = {
    "Einkaufen": ["EDEKA", "ALDI", "LIDL"],
    "Mobilität": ["ARAL", "SHELL", "DEUTSCHE BAHN"],
    "Freizeit": ["NETFLIX", "KINO"],
    "Gehalt": ["GEHALT"],
    "Miete": ["MIETE"],
}


# Finanzkonten, die für die Demo-Benutzer angelegt werden.
DEMO_ACCOUNTS = {
    "anna.mueller@example.com": ["Girokonto", "Sparkonto"],
    "ben.schmidt@example.com": ["Girokonto"],
    "clara.weiss@example.com": ["Alltagskonto"],
}


# Betrag, Empfänger, Verwendungszweck, Kategorie
DEMO_ENTRIES = [
    (Decimal("2450.00"), "Arbeitgeber GmbH", "Gehalt Juli", "Gehalt"),
    (Decimal("-62.45"), "EDEKA Hildesheim", "Wocheneinkauf", "Einkaufen"),
    (Decimal("-740.00"), "Hausverwaltung Nord", "Miete Juli", "Miete"),
    (Decimal("-18.99"), "Netflix", "Monatsabo", "Freizeit"),
    (Decimal("-54.10"), "ARAL", "Tanken", "Mobilität"),
    (Decimal("-12.80"), "Campus Mensa", "Mittagessen", "Nicht kategorisiert"),
    (Decimal("-31.50"), "LIDL", "Lebensmittel", "Einkaufen"),
    (Decimal("-9.90"), "Kino Hildesheim", "Kinokarte", "Freizeit"),
    (Decimal("-29.00"), "Deutsche Bahn", "Fahrkarte", "Mobilität"),
    (Decimal("-15.20"), "EDEKA", "Getränke", "Einkaufen"),
    (Decimal("-8.50"), "Bäckerei", "Frühstück", "Nicht kategorisiert"),
    (Decimal("-47.80"), "ALDI", "Wocheneinkauf", "Einkaufen"),
    (Decimal("-22.00"), "Sportverein", "Monatsbeitrag", "Nicht kategorisiert"),
    (Decimal("-13.40"), "SHELL", "Tanken", "Mobilität"),
    (Decimal("-6.99"), "Streamingdienst", "Musikabo", "Nicht kategorisiert"),
    (Decimal("-28.70"), "LIDL", "Lebensmittel", "Einkaufen"),
    (Decimal("-45.00"), "Restaurant", "Abendessen", "Nicht kategorisiert"),
    (Decimal("-19.50"), "Kino", "Filmabend", "Freizeit"),
    (Decimal("-7.20"), "Campus Mensa", "Mittagessen", "Nicht kategorisiert"),
    (Decimal("-36.10"), "EDEKA", "Wocheneinkauf", "Einkaufen"),
]


def validate_demo_configuration():
    """Prüft die Demodaten, bevor die bestehende Datenbank zurückgesetzt wird."""
    available_categories = set(DEFAULT_CATEGORIES)
    referenced_categories = set(KEYWORDS)
    referenced_categories.update(entry[3] for entry in DEMO_ENTRIES)

    missing_categories = sorted(referenced_categories - available_categories)
    if missing_categories:
        raise RuntimeError(
            "Folgende Kategorien werden in Schlagwörtern oder Buchungen verwendet, "
            "aber nicht in DEFAULT_CATEGORIES angelegt: "
            + ", ".join(missing_categories)
        )

    demo_user_emails = {user[0] for user in DEMO_USERS}
    missing_users = sorted(set(DEMO_ACCOUNTS) - demo_user_emails)
    if missing_users:
        raise RuntimeError(
            "Für folgende unbekannte Demo-Benutzer wurden Finanzkonten definiert: "
            + ", ".join(missing_users)
        )


def initialize_database():
    """Erstellt das Schema neu und fügt ausschließlich fiktive Demodaten ein."""
    SecurityService.ensure_hash_method_available()
    validate_demo_configuration()

    database = Database()
    schema_path = BASE_DIR / "database" / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")

    # Das Schema wird zuerst vollständig neu erstellt.
    with database.cursor(commit=True, dict_rows=False) as cursor:
        cursor.execute(schema)

    customer_ids = {}
    category_ids = {}
    account_ids = {}

    # Alle Demodaten werden in einer gemeinsamen Transaktion eingefügt.
    with database.cursor(commit=True) as cursor:
        # Benutzer, Passwörter, Kategorien und Schlagwörter
        for email, first_name, last_name, age, bank_name, password in DEMO_USERS:
            cursor.execute(
                """
                INSERT INTO kunde (email, vorname, nachname, alter, bankinstitut)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING kundenid
                """,
                (email, first_name, last_name, age, bank_name),
            )
            customer_id = cursor.fetchone()["kundenid"]
            customer_ids[email] = customer_id

            cursor.execute(
                """
                INSERT INTO passwort (kundenid, passwort_hash)
                VALUES (%s, %s)
                """,
                (customer_id, SecurityService.hash_password(password)),
            )

            category_ids[customer_id] = {}
            for category_name in DEFAULT_CATEGORIES:
                cursor.execute(
                    """
                    INSERT INTO kategorie (kundenid, bezeichnung, ist_standard)
                    VALUES (%s, %s, TRUE)
                    RETURNING kategorieid
                    """,
                    (customer_id, category_name),
                )
                category_id = cursor.fetchone()["kategorieid"]
                category_ids[customer_id][category_name] = category_id

            for category_name, keywords in KEYWORDS.items():
                category_id = category_ids[customer_id].get(category_name)
                if category_id is None:
                    raise RuntimeError(
                        f"Die Kategorie '{category_name}' wurde für '{email}' "
                        "nicht angelegt."
                    )

                for word in keywords:
                    cursor.execute(
                        """
                        INSERT INTO schlagwort (kategorieid, wort)
                        VALUES (%s, %s)
                        """,
                        (category_id, word),
                    )

        # Finanzkonten
        for email, account_names in DEMO_ACCOUNTS.items():
            account_ids[email] = []
            for account_name in account_names:
                cursor.execute(
                    """
                    INSERT INTO konto (kundenid, kontoname)
                    VALUES (%s, %s)
                    RETURNING kontoid
                    """,
                    (customer_ids[email], account_name),
                )
                account_ids[email].append(cursor.fetchone()["kontoid"])

        # Buchungen für Annas erstes Finanzkonto
        anna_email = "anna.mueller@example.com"
        anna_id = customer_ids[anna_email]
        anna_giro_id = account_ids[anna_email][0]
        start_time = datetime.now().replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )

        for index, (amount, recipient, purpose, category_name) in enumerate(DEMO_ENTRIES):
            category_id = category_ids[anna_id].get(category_name)
            if category_id is None:
                raise RuntimeError(
                    f"Die Kategorie '{category_name}' wurde für die Demobuchung "
                    "nicht angelegt."
                )

            cursor.execute(
                """
                INSERT INTO kontoeintrag
                    (kontoid, kategorieid, wertstellungsdatum,
                     betrag, empfaenger, verwendungszweck)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    anna_giro_id,
                    category_id,
                    start_time - timedelta(days=index * 3),
                    amount,
                    recipient,
                    purpose,
                ),
            )

        # Demo-Gruppe mit Anna und Ben
        cursor.execute(
            """
            INSERT INTO benutzergruppe (gruppenname, erstellt_von)
            VALUES (%s, %s)
            RETURNING gruppenid
            """,
            ("WG Finanzen", anna_id),
        )
        group_id = cursor.fetchone()["gruppenid"]

        member_ids = [
            anna_id,
            customer_ids["ben.schmidt@example.com"],
        ]
        for member_id in member_ids:
            cursor.execute(
                """
                INSERT INTO gruppenmitglied (gruppenid, kundenid)
                VALUES (%s, %s)
                """,
                (group_id, member_id),
            )

    print("Datenbank wurde neu erstellt und mit Demodaten gefüllt.")
    print("Demo-Anmeldung: anna.mueller@example.com / AnnaTest!123")


if __name__ == "__main__":
    initialize_database()