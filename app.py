
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# ==================================================
# تنظیمات امنیتی
# ==================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-this"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "1234"
)

# ==================================================
# دیتابیس
# ==================================================

DATABASE = "messages.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ساخت جدول هنگام اجرای برنامه
init_db()


# ==================================================
# محافظت از Admin
# ==================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return wrapper


# ==================================================
# صفحات سایت
# ==================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/questions")
def questions():
    return render_template("questions.html")


@app.route("/question2")
def question2():
    return render_template("question2.html")


@app.route("/final")
def final():
    return render_template("final.html")


# ==================================================
# دریافت پیام
# ==================================================

@app.route("/send-message", methods=["POST"])
def send_message():

    message = request.form.get("message", "").strip()

    if not message:
        return redirect(url_for("final"))

    connection = get_db()

    connection.execute(
        """
        INSERT INTO messages (message, created_at)
        VALUES (?, ?)
        """,
        (
            message,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    connection.commit()
    connection.close()

    return render_template(
        "final.html",
        sent=True
    )


# ==================================================
# ADMIN LOGIN
# ==================================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_logged_in"):
        return redirect(url_for("admin_panel"))

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(url_for("admin_panel"))

        return render_template(
            "admin.html",
            error="رمز عبور اشتباه است."
        )

    return render_template("admin.html")


# ==================================================
# ADMIN PANEL
# ==================================================

@app.route("/admin/messages")
@login_required
def admin_panel():

    connection = get_db()

    messages = connection.execute(
        """
        SELECT *
        FROM messages
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        messages=messages,
        logged_in=True
    )


# ==================================================
# حذف پیام
# ==================================================

@app.route("/admin/delete/<int:message_id>", methods=["POST"])
@login_required
def delete_message(message_id):

    connection = get_db()

    connection.execute(
        """
        DELETE FROM messages
        WHERE id = ?
        """,
        (message_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin_panel"))


# ==================================================
# خروج از پنل
# ==================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("admin_login"))


# ==================================================
# اجرای برنامه
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
```
