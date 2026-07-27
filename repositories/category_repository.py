from database.connection import Database


class CategoryRepository:
    """SQL-Abfragen für Kategorien und Schlagwörter."""
    def __init__(self, database=None):
        self.database = database or Database()

    def create_default_categories(self, customer_id):
        defaults = [
            "Nicht kategorisiert",
            "Einkaufen",
            "Miete",
            "Mobilität",
            "Freizeit",
            "Gehalt",
        ]
        with self.database.cursor(commit=True) as cursor:
            for name in defaults:
                cursor.execute(
                    """
                    INSERT INTO kategorie (kundenid, bezeichnung, ist_standard)
                    VALUES (%s, %s, TRUE)
                    ON CONFLICT (kundenid, bezeichnung) DO NOTHING
                    """,
                    (customer_id, name),
                )

    def list_for_user(self, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT k.kategorieid, k.bezeichnung,
                       COALESCE(
                           (
                               SELECT JSON_AGG(
                                   JSON_BUILD_OBJECT(
                                       'schlagwortid', s.schlagwortid,
                                       'wort', s.wort
                                   ) ORDER BY s.wort
                               )
                               FROM schlagwort s
                               WHERE s.kategorieid = k.kategorieid
                           ),
                           '[]'
                       ) AS schlagwoerter
                FROM kategorie k
                WHERE k.kundenid = %s
                ORDER BY k.bezeichnung
                """,
                (customer_id,),
            )
            return cursor.fetchall()

    def create(self, customer_id, name):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO kategorie (kundenid, bezeichnung)
                VALUES (%s, %s)
                RETURNING kategorieid
                """,
                (customer_id, name),
            )
            return cursor.fetchone()["kategorieid"]

    def belongs_to_user(self, category_id, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM kategorie
                WHERE kategorieid = %s AND kundenid = %s
                """,
                (category_id, customer_id),
            )
            return cursor.fetchone() is not None


    def update_category(self, category_id, customer_id, name):
        """Benennt eine eigene, bearbeitbare Kategorie um."""
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE kategorie
                SET bezeichnung = %s
                WHERE kategorieid = %s
                  AND kundenid = %s
                  AND bezeichnung <> 'Nicht kategorisiert'
                """,
                (name, category_id, customer_id),
            )
            return cursor.rowcount > 0

    def update_keyword(self, keyword_id, customer_id, word):
        """Ändert ein Schlagwort, wenn die zugehörige Kategorie dem Nutzer gehört."""
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE schlagwort s
                SET wort = %s
                FROM kategorie k
                WHERE s.schlagwortid = %s
                  AND s.kategorieid = k.kategorieid
                  AND k.kundenid = %s
                  AND k.bezeichnung <> 'Nicht kategorisiert'
                """,
                (word, keyword_id, customer_id),
            )
            return cursor.rowcount > 0

    def add_keyword(self, category_id, word):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO schlagwort (kategorieid, wort)
                VALUES (%s, %s)
                RETURNING schlagwortid
                """,
                (category_id, word),
            )
            return cursor.fetchone()["schlagwortid"]

    def delete_keyword(self, keyword_id, customer_id):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                DELETE FROM schlagwort s
                USING kategorie k
                WHERE s.schlagwortid = %s
                  AND s.kategorieid = k.kategorieid
                  AND k.kundenid = %s
                """,
                (keyword_id, customer_id),
            )
            return cursor.rowcount > 0

    def delete_category(self, category_id, customer_id):
        """Ordnet Buchungen der Systemkategorie zu und löscht danach die Kategorie."""
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                SELECT kategorieid, bezeichnung
                FROM kategorie
                WHERE kategorieid = %s AND kundenid = %s
                FOR UPDATE
                """,
                (category_id, customer_id),
            )
            category = cursor.fetchone()
            if category is None:
                return None
            if category["bezeichnung"] == "Nicht kategorisiert":
                raise ValueError("Die Systemkategorie kann nicht gelöscht werden.")

            cursor.execute(
                """
                SELECT kategorieid
                FROM kategorie
                WHERE kundenid = %s AND bezeichnung = 'Nicht kategorisiert'
                FOR UPDATE
                """,
                (customer_id,),
            )
            fallback = cursor.fetchone()
            if fallback is None:
                raise RuntimeError("Die technische Auffangkategorie fehlt.")

            cursor.execute(
                "SELECT COUNT(*) AS anzahl FROM kontoeintrag WHERE kategorieid = %s",
                (category_id,),
            )
            usage = cursor.fetchone()["anzahl"]

            cursor.execute(
                "UPDATE kontoeintrag SET kategorieid = %s WHERE kategorieid = %s",
                (fallback["kategorieid"], category_id),
            )
            cursor.execute(
                "DELETE FROM kategorie WHERE kategorieid = %s AND kundenid = %s",
                (category_id, customer_id),
            )
            return {
                "bezeichnung": category["bezeichnung"],
                "anzahl_buchungen": usage,
            }

    def find_matching_category(self, customer_id, recipient, purpose):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT k.kategorieid, k.bezeichnung, s.wort
                FROM schlagwort s
                JOIN kategorie k ON k.kategorieid = s.kategorieid
                WHERE k.kundenid = %s
                  AND (
                    %s ILIKE '%%' || s.wort || '%%'
                    OR %s ILIKE '%%' || s.wort || '%%'
                  )
                ORDER BY LENGTH(s.wort) DESC, s.schlagwortid
                LIMIT 1
                """,
                (customer_id, recipient, purpose),
            )
            return cursor.fetchone()

    def get_uncategorized_id(self, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT kategorieid
                FROM kategorie
                WHERE kundenid = %s AND bezeichnung = 'Nicht kategorisiert'
                """,
                (customer_id,),
            )
            row = cursor.fetchone()
            return row["kategorieid"] if row else None
