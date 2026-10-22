import re
import unittest
import bcrypt
from app import create_app
from app.db import DuplicateEmail


class FakeRepo:
    def __init__(self):
        self.rows = {}

    def email_exists(self, email):
        return email in self.rows

    def create_guest(self, name, email, phone, password_hash):
        if email in self.rows:
            raise DuplicateEmail()
        self.rows[email] = dict(name=name, phone=phone, hash=password_hash)
        return len(self.rows)


GOOD = dict(name="Ali Hassan", email="Ali@Example.com", phone="+249912345678",
            password="Str0ngPass!", consent="on")


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.repo = FakeRepo()
        self.client = create_app(repo=self.repo, testing=True).test_client()

    def post(self, **over):
        html = self.client.get("/register").get_data(as_text=True)
        token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
        data = dict(GOOD, csrf_token=token)
        data.update(over)
        data = {k: v for k, v in data.items() if v is not None}
        return self.client.post("/register", data=data)

    def test_01_page_loads_with_notice_and_checkbox(self):
        html = self.client.get("/register").get_data(as_text=True)
        self.assertIn("privacy notice", html)
        self.assertIn('name="consent"', html)

    def test_02_success(self):
        r = self.post()
        self.assertEqual(r.status_code, 201)
        self.assertIn("ali@example.com", self.repo.rows)

    def test_03_name_required(self):
        self.assertEqual(self.post(name="").status_code, 400)

    def test_04_email_required(self):
        self.assertEqual(self.post(email="").status_code, 400)

    def test_05_email_invalid(self):
        self.assertEqual(self.post(email="not-an-email").status_code, 400)

    def test_06_phone_required(self):
        self.assertEqual(self.post(phone="").status_code, 400)

    def test_07_phone_invalid(self):
        self.assertEqual(self.post(phone="abc123").status_code, 400)

    def test_08_password_required(self):
        self.assertEqual(self.post(password="").status_code, 400)

    def test_09_password_too_short(self):
        self.assertEqual(self.post(password="short1").status_code, 400)

    def test_10_consent_required(self):
        r = self.post(consent=None)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(len(self.repo.rows), 0)

    def test_11_duplicate_email_rejected(self):
        self.post()
        r = self.post()
        self.assertEqual(r.status_code, 409)
        self.assertIn("already registered", r.get_data(as_text=True))

    def test_12_duplicate_email_case_insensitive(self):
        self.post(email="a@b.com")
        self.assertEqual(self.post(email="A@B.COM").status_code, 409)

    def test_13_password_stored_hashed_bcrypt(self):
        self.post()
        h = self.repo.rows["ali@example.com"]["hash"]
        self.assertNotIn("Str0ngPass!", h)
        self.assertTrue(h.startswith("$2"))
        self.assertTrue(bcrypt.checkpw(b"Str0ngPass!", h.encode()))

    def test_14_same_password_different_hash(self):
        self.post(email="a@x.com")
        self.post(email="b@x.com")
        self.assertNotEqual(self.repo.rows["a@x.com"]["hash"], self.repo.rows["b@x.com"]["hash"])

    def test_15_csrf_missing_rejected(self):
        r = self.client.post("/register", data=dict(GOOD))
        self.assertEqual(r.status_code, 400)

    def test_16_xss_escaped(self):
        r = self.post(name="<script>alert(1)</script>", email="bad")
        self.assertNotIn("<script>alert(1)</script>", r.get_data(as_text=True))

    def test_17_error_keeps_input_not_password(self):
        r = self.post(email="bad", password="Str0ngPass!")
        html = r.get_data(as_text=True)
        self.assertIn("Ali Hassan", html)
        self.assertNotIn("Str0ngPass!", html)

    def test_18_sql_injection_text_is_just_data(self):
        r = self.post(name="x'; DROP TABLE Guest;--")
        self.assertEqual(r.status_code, 201)

    def test_19_security_headers(self):
        r = self.client.get("/register")
        self.assertEqual(r.headers["X-Frame-Options"], "DENY")

    def test_20_no_ssn_field(self):
        html = self.client.get("/register").get_data(as_text=True)
        self.assertNotIn("ssn", html.lower())


if __name__ == "__main__":
    unittest.main()
