from database.connection import Database


class UserRepository:
    """SQL-Abfragen für Benutzer und Passwörter."""

    def __init__(self, database=None):
        self.database = database or Database()

    def find_by_email(self, email):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT k.kundenid, k.email, k.vorname, k.nachname,
                       k.alter, k.bankinstitut, p.passwort_hash
                FROM kunde k
                JOIN passwort p ON p.kundenid = k.kundenid
                WHERE LOWER(k.email) = LOWER(%s)
                """,
                (email,),
            )
            return cursor.fetchone()

    def find_by_id(self, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT kundenid, email, vorname, nachname, alter, bankinstitut
                FROM kunde
                WHERE kundenid = %s
                """,
                (customer_id,),
            )
            return cursor.fetchone()

    def find_auth_by_id(self, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT k.kundenid, k.email, k.vorname, k.nachname,
                       k.alter, k.bankinstitut, p.passwort_hash
                FROM kunde k
                JOIN passwort p ON p.kundenid = k.kundenid
                WHERE k.kundenid = %s
                """,
                (customer_id,),
            )
            return cursor.fetchone()

    def email_exists(self, email):
        with self.database.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM kunde WHERE LOWER(email) = LOWER(%s)",
                (email,),
            )
            return cursor.fetchone() is not None

    def create(self, *, first_name, last_name, email, password_hash, age, bank_name):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO kunde (email, vorname, nachname, alter, bankinstitut)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING kundenid
                """,
                (email, first_name, last_name, age, bank_name),
            )
            customer_id = cursor.fetchone()["kundenid"]
            cursor.execute(
                "INSERT INTO passwort (kundenid, passwort_hash) VALUES (%s, %s)",
                (customer_id, password_hash),
            )
            return customer_id

    def update_profile(self, customer_id, *, first_name, last_name, age, bank_name):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE kunde
                SET vorname = %s,
                    nachname = %s,
                    alter = %s,
                    bankinstitut = %s
                WHERE kundenid = %s
                """,
                (first_name, last_name, age, bank_name, customer_id),
            )
            return cursor.rowcount > 0

    def update_password_hash(self, customer_id, password_hash):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE passwort
                SET passwort_hash = %s
                WHERE kundenid = %s
                """,
                (password_hash, customer_id),
            )
            return cursor.rowcount > 0

    def delete(self, customer_id):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM kunde WHERE kundenid = %s", (customer_id,))
            return cursor.rowcount > 0
