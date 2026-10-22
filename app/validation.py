"""Input validation for guest registration (US1, FR1)."""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")


def validate_registration(form):
    """Return (clean_data, errors). errors maps field -> message."""
    errors = {}
    name = (form.get("name") or "").strip()
    email = (form.get("email") or "").strip().lower()
    phone = (form.get("phone") or "").strip().replace(" ", "").replace("-", "")
    password = form.get("password") or ""
    consent = form.get("consent") == "on"

    if not name:
        errors["name"] = "Name is required."
    elif len(name) > 100:
        errors["name"] = "Name is too long (max 100 characters)."
    if not email:
        errors["email"] = "Email is required."
    elif len(email) > 100 or not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."
    if not phone:
        errors["phone"] = "Phone number is required."
    elif not PHONE_RE.match(phone):
        errors["phone"] = "Enter a valid phone number (7 to 15 digits)."
    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 8:
        errors["password"] = "Password must have at least 8 characters."
    elif len(password.encode("utf-8")) > 72:
        errors["password"] = "Password is too long (max 72 bytes)."
    if not consent:
        errors["consent"] = "You must accept the privacy notice to register."

    return {"name": name, "email": email, "phone": phone, "password": password}, errors
