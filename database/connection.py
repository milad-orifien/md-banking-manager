from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from config import Config


class Database:
    """Öffnet eine Verbindung zur PostgreSQL-Datenbank."""

    def __init__(self, db_config=None):
        self.db_config = db_config or Config.DB_CONFIG

    @contextmanager
    def cursor(self, *, commit=False, dict_rows=True):
        connection = psycopg2.connect(**self.db_config)
        cursor_factory = psycopg2.extras.RealDictCursor if dict_rows else None
        cursor = connection.cursor(cursor_factory=cursor_factory)

        try:
            yield cursor
            if commit:
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
