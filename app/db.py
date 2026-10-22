"""MySQL access. All queries are parameterized (no string concatenation)."""
import os
import mysql.connector
from mysql.connector import errorcode


class DuplicateEmail(Exception):
    pass


class GuestRepository:
    def _connect(self):
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ.get("DB_NAME", "hotel_system_db"),
        )

    def email_exists(self, email):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM Guest WHERE Email = %s", (email,))
            return cur.fetchone() is not None
        finally:
            conn.close()

    def create_guest(self, name, email, phone, password_hash):
        """Insert a new guest; the consent time is stored (P2). Returns Guest_ID."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Guest (Name, Email, Phone, Password_Hash, Privacy_Consent_At) "
                "VALUES (%s, %s, %s, %s, NOW())",
                (name, email, phone, password_hash),
            )
            conn.commit()
            return cur.lastrowid
        except mysql.connector.Error as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                raise DuplicateEmail() from e
            raise
        finally:
            conn.close()
