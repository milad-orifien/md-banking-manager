from database.connection import Database


class CommunityRepository:
    """SQL-Abfragen für Gruppen und Nachrichten."""
    def __init__(self, database=None):
        self.database = database or Database()

    def create_group(self, creator_id, name):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO benutzergruppe (gruppenname, erstellt_von)
                VALUES (%s, %s)
                RETURNING gruppenid
                """,
                (name, creator_id),
            )
            group_id = cursor.fetchone()["gruppenid"]
            cursor.execute(
                """
                INSERT INTO gruppenmitglied (gruppenid, kundenid)
                VALUES (%s, %s)
                """,
                (group_id, creator_id),
            )
            return group_id

    def list_groups_for_user(self, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT g.gruppenid, g.gruppenname,
                       (
                           SELECT COUNT(*)
                           FROM gruppenmitglied gm_count
                           WHERE gm_count.gruppenid = g.gruppenid
                       ) AS mitgliederzahl,
                       (
                           SELECT COUNT(ko.kontoid)
                           FROM gruppenmitglied gm_accounts
                           JOIN konto ko ON ko.kundenid = gm_accounts.kundenid
                           WHERE gm_accounts.gruppenid = g.gruppenid
                       ) AS kontenzahl
                FROM benutzergruppe g
                JOIN gruppenmitglied gm ON gm.gruppenid = g.gruppenid
                WHERE gm.kundenid = %s
                ORDER BY g.gruppenname
                """,
                (customer_id,),
            )
            return cursor.fetchall()

    def get_group(self, group_id, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT g.gruppenid, g.gruppenname
                FROM benutzergruppe g
                JOIN gruppenmitglied gm ON gm.gruppenid = g.gruppenid
                WHERE g.gruppenid = %s AND gm.kundenid = %s
                """,
                (group_id, customer_id),
            )
            return cursor.fetchone()

    def list_group_members(self, group_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT k.kundenid, k.vorname, k.nachname, k.email
                FROM gruppenmitglied gm
                JOIN kunde k ON k.kundenid = gm.kundenid
                WHERE gm.gruppenid = %s
                ORDER BY k.nachname, k.vorname
                """,
                (group_id,),
            )
            return cursor.fetchall()

    def is_member(self, group_id, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM gruppenmitglied
                WHERE gruppenid = %s AND kundenid = %s
                """,
                (group_id, customer_id),
            )
            return cursor.fetchone() is not None

    def create_invitation(self, group_id, creator_id, recipient_id, token):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO gruppeneinladung
                    (gruppenid, erstellt_von, empfaengerid, token)
                VALUES (%s, %s, %s, %s)
                RETURNING einladungid
                """,
                (group_id, creator_id, recipient_id, token),
            )
            return cursor.fetchone()["einladungid"]

    def get_invitation(self, token):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.einladungid, e.gruppenid, e.empfaengerid,
                       e.angenommen, g.gruppenname
                FROM gruppeneinladung e
                JOIN benutzergruppe g ON g.gruppenid = e.gruppenid
                WHERE e.token = %s
                """,
                (token,),
            )
            return cursor.fetchone()

    def accept_invitation(self, invitation_id, group_id, customer_id):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO gruppenmitglied (gruppenid, kundenid)
                VALUES (%s, %s)
                ON CONFLICT (gruppenid, kundenid) DO NOTHING
                """,
                (group_id, customer_id),
            )
            cursor.execute(
                """
                UPDATE gruppeneinladung
                SET angenommen = TRUE
                WHERE einladungid = %s
                """,
                (invitation_id,),
            )

    def send_message(self, sender_id, recipient_id, subject, content, invitation_id=None):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO nachricht
                    (absenderid, empfaengerid, betreff, inhalt, einladungid)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING nachrichtid
                """,
                (sender_id, recipient_id, subject, content, invitation_id),
            )
            return cursor.fetchone()["nachrichtid"]

    def list_inbox(self, customer_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT n.nachrichtid, n.betreff, n.inhalt, n.gelesen,
                       n.gesendet_am, n.einladungid,
                       k.vorname AS absender_vorname,
                       k.nachname AS absender_nachname,
                       CASE WHEN e.angenommen = FALSE THEN e.token END AS einladung_token
                FROM nachricht n
                JOIN kunde k ON k.kundenid = n.absenderid
                LEFT JOIN gruppeneinladung e ON e.einladungid = n.einladungid
                WHERE n.empfaengerid = %s
                ORDER BY n.gesendet_am DESC
                """,
                (customer_id,),
            )
            return cursor.fetchall()

    def mark_read(self, message_id, customer_id):
        with self.database.cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE nachricht SET gelesen = TRUE
                WHERE nachrichtid = %s AND empfaengerid = %s
                """,
                (message_id, customer_id),
            )

    def users_share_group(self, viewer_id, owner_id, group_id):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM gruppenmitglied a
                JOIN gruppenmitglied b ON b.gruppenid = a.gruppenid
                WHERE a.gruppenid = %s
                  AND a.kundenid = %s
                  AND b.kundenid = %s
                """,
                (group_id, viewer_id, owner_id),
            )
            return cursor.fetchone() is not None
