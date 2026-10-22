import os
import secrets
import bcrypt
from flask import Flask, render_template, request, session, abort, redirect, url_for, flash

from .validation import validate_registration
from .db import GuestRepository, DuplicateEmail


def create_app(repo=None, testing=False):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config["TESTING"] = testing
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.repo = repo or GuestRepository()

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        return session["csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.after_request
    def headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'"
        return resp

    @app.route("/")
    def index():
        return redirect(url_for("register"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html", errors={}, values={})
        sent = request.form.get("csrf_token", "")
        if not sent or not secrets.compare_digest(sent, session.get("csrf", "")):
            abort(400)
        data, errors = validate_registration(request.form)
        values = {k: data[k] for k in ("name", "email", "phone")}
        if errors:
            return render_template("register.html", errors=errors, values=values), 400
        if app.repo.email_exists(data["email"]):
            errors["email"] = "This email is already registered."
            return render_template("register.html", errors=errors, values=values), 409
        pw_hash = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("ascii")
        try:
            app.repo.create_guest(data["name"], data["email"], data["phone"], pw_hash)
        except DuplicateEmail:
            errors["email"] = "This email is already registered."
            return render_template("register.html", errors=errors, values=values), 409
        return render_template("success.html", name=data["name"]), 201

    return app
