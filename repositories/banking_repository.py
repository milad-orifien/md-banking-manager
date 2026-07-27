from database.connection import Database


class BankingRepository:
    """SQL-Abfragen für Finanzkonten und Buchungen."""
    SORT_COLUMNS = {
        "datum": "ke.wertstellungsdatum",
        "betrag": "ke.betrag",
        "empfaenger": "ke.empfaenger",
        "verwendungszweck": "ke.verwendungszweck",
        "kategorie": "COALESCE(k.bezeichnung, 'Nicht kategorisiert')",
    }

    def __init__(self, database=None):
        self.database = database or Database()

    def create_account(self, customer_id, name):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO konto (kundenid, kontoname)
                VALUES (%s, %s)
                RETURNING kontoid
                """,
                (customer_id, name),
            )
            return cursor.fetchone()["kontoid"]


    def update_account_name(self, account_id, customer_id, name):
        """Benennt ein eigenes Finanzkonto um."""
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE konto
                SET kontoname = %s
                WHERE kontoid = %s AND kundenid = %s
                """,
                (name, account_id, customer_id),
            )
            return cursor.rowcount > 0

    def account_belongs_to_user(self, account_id, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM konto WHERE kontoid = %s AND kundenid = %s",
                (account_id, customer_id),
            )
            return cursor.fetchone() is not None

    def delete_account(self, account_id, customer_id):
        """Löscht ein eigenes Finanzkonto samt Buchungen in einer Transaktion."""
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                SELECT ko.kontoid, ko.kontoname,
                       (SELECT COUNT(*) FROM kontoeintrag ke WHERE ke.kontoid = ko.kontoid)
                           AS anzahl_eintraege
                FROM konto ko
                WHERE ko.kontoid = %s AND ko.kundenid = %s
                FOR UPDATE
                """,
                (account_id, customer_id),
            )
            account = cursor.fetchone()
            if account is None:
                return None

            cursor.execute(
                "DELETE FROM konto WHERE kontoid = %s AND kundenid = %s",
                (account_id, customer_id),
            )
            return account

    def get_account(self, account_id, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT ko.kontoid, ko.kundenid, ko.kontoname,
                       COALESCE(SUM(ke.betrag), 0) AS kontostand,
                       COUNT(ke.eintragid) AS anzahl_eintraege
                FROM konto ko
                LEFT JOIN kontoeintrag ke ON ke.kontoid = ko.kontoid
                WHERE ko.kontoid = %s AND ko.kundenid = %s
                GROUP BY ko.kontoid
                """,
                (account_id, customer_id),
            )
            return cursor.fetchone()

    def list_accounts(self, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT ko.kontoid, ko.kontoname,
                       COALESCE(SUM(ke.betrag), 0) AS kontostand,
                       COUNT(ke.eintragid) AS anzahl_eintraege
                FROM konto ko
                LEFT JOIN kontoeintrag ke ON ke.kontoid = ko.kontoid
                WHERE ko.kundenid = %s
                GROUP BY ko.kontoid
                ORDER BY ko.kontoname
                """,
                (customer_id,),
            )
            return cursor.fetchall()

    def list_latest_entries(self, customer_id, limit=5):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT ke.eintragid, ke.wertstellungsdatum, ke.betrag,
                       ke.empfaenger, ke.verwendungszweck,
                       ko.kontoid, ko.kontoname,
                       COALESCE(k.bezeichnung, 'Nicht kategorisiert') AS kategorie
                FROM kontoeintrag ke
                JOIN konto ko ON ko.kontoid = ke.kontoid
                LEFT JOIN kategorie k ON k.kategorieid = ke.kategorieid
                WHERE ko.kundenid = %s
                ORDER BY ke.wertstellungsdatum DESC, ke.eintragid DESC
                LIMIT %s
                """,
                (customer_id, limit),
            )
            return cursor.fetchall()

    def create_entry(
        self,
        *,
        account_id,
        category_id,
        value_date,
        amount,
        recipient,
        purpose,
    ):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO kontoeintrag
                    (kontoid, kategorieid, wertstellungsdatum, betrag, empfaenger, verwendungszweck)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING eintragid
                """,
                (account_id, category_id, value_date, amount, recipient, purpose),
            )
            return cursor.fetchone()["eintragid"]

    def update_entry_category(self, entry_id, category_id, customer_id):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE kontoeintrag ke
                SET kategorieid = %s
                FROM konto ko
                WHERE ke.eintragid = %s
                  AND ke.kontoid = ko.kontoid
                  AND ko.kundenid = %s
                """,
                (category_id, entry_id, customer_id),
            )
            return cursor.rowcount > 0

    def list_entries(
        self,
        *,
        account_id,
        filters,
        sort_key="datum",
        direction="desc",
        limit=15,
    ):
        where = ["ke.kontoid = %s"]
        params = [account_id]

        if filters.get("purpose"):
            where.append("ke.verwendungszweck ILIKE %s")
            params.append(f"%{filters['purpose']}%")
        if filters.get("recipient"):
            where.append("ke.empfaenger ILIKE %s")
            params.append(f"%{filters['recipient']}%")
        if filters.get("date_from"):
            where.append("ke.wertstellungsdatum::date >= %s")
            params.append(filters["date_from"])
        if filters.get("date_to"):
            where.append("ke.wertstellungsdatum::date <= %s")
            params.append(filters["date_to"])
        if filters.get("amount_min") is not None:
            where.append("ke.betrag >= %s")
            params.append(filters["amount_min"])
        if filters.get("amount_max") is not None:
            where.append("ke.betrag <= %s")
            params.append(filters["amount_max"])

        order_column = self.SORT_COLUMNS.get(sort_key, self.SORT_COLUMNS["datum"])
        order_direction = "ASC" if direction == "asc" else "DESC"
        limit_clause = ""
        if limit is not None:
            limit_clause = "LIMIT %s"
            params.append(limit)

        query = f"""
            SELECT ke.eintragid, ke.wertstellungsdatum, ke.betrag,
                   ke.empfaenger, ke.verwendungszweck, ke.kategorieid,
                   COALESCE(k.bezeichnung, 'Nicht kategorisiert') AS kategorie
            FROM kontoeintrag ke
            LEFT JOIN kategorie k ON k.kategorieid = ke.kategorieid
            WHERE {' AND '.join(where)}
            ORDER BY {order_column} {order_direction}, ke.eintragid {order_direction}
            {limit_clause}
        """

        with self.database.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    def count_and_sum_entries(self, account_id, filters):
        where = ["ke.kontoid = %s"]
        params = [account_id]
        mapping = [
            ("purpose", "ke.verwendungszweck ILIKE %s", lambda v: f"%{v}%"),
            ("recipient", "ke.empfaenger ILIKE %s", lambda v: f"%{v}%"),
            ("date_from", "ke.wertstellungsdatum::date >= %s", lambda v: v),
            ("date_to", "ke.wertstellungsdatum::date <= %s", lambda v: v),
            ("amount_min", "ke.betrag >= %s", lambda v: v),
            ("amount_max", "ke.betrag <= %s", lambda v: v),
        ]
        for key, clause, transform in mapping:
            value = filters.get(key)
            if value not in (None, ""):
                where.append(clause)
                params.append(transform(value))

        with self.database.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT COUNT(*) AS anzahl,
                       COALESCE(SUM(ke.betrag), 0) AS summe
                FROM kontoeintrag ke
                WHERE {' AND '.join(where)}
                """,
                tuple(params),
            )
            return cursor.fetchone()

    def report_expenses(self, customer_id, date_from=None, date_to=None, account_id=None):
        where = ["ko.kundenid = %s", "ke.betrag < 0"]
        params = [customer_id]
        if date_from:
            where.append("ke.wertstellungsdatum::date >= %s")
            params.append(date_from)
        if date_to:
            where.append("ke.wertstellungsdatum::date <= %s")
            params.append(date_to)
        if account_id:
            where.append("ko.kontoid = %s")
            params.append(account_id)

        with self.database.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT COALESCE(k.bezeichnung, 'Nicht kategorisiert') AS kategorie,
                       SUM(ABS(ke.betrag)) AS summe
                FROM kontoeintrag ke
                JOIN konto ko ON ko.kontoid = ke.kontoid
                LEFT JOIN kategorie k ON k.kategorieid = ke.kategorieid
                WHERE {' AND '.join(where)}
                GROUP BY COALESCE(k.bezeichnung, 'Nicht kategorisiert')
                ORDER BY summe DESC
                """,
                tuple(params),
            )
            return cursor.fetchall()

    def list_all_entries_for_export(self, account_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT ke.wertstellungsdatum, ke.betrag, ke.empfaenger,
                       ke.verwendungszweck,
                       COALESCE(k.bezeichnung, 'Nicht kategorisiert') AS kategorie
                FROM kontoeintrag ke
                LEFT JOIN kategorie k ON k.kategorieid = ke.kategorieid
                WHERE ke.kontoid = %s
                ORDER BY ke.wertstellungsdatum, ke.eintragid
                """,
                (account_id,),
            )
            return cursor.fetchall()
