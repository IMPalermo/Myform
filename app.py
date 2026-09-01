from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from functools import wraps
from datetime import datetime


app = Flask(__name__)

# کلید امنیتی Flask
# بعداً وقتی سایت رو آنلاین کردیم، این مقدار رو در Environment Variable قرار می‌دیم.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-this"
)


# رمز ورود به پنل مدیریت
# برای تست روی کامپیوتر:
ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "1234"
)


# اسم دیتابیس
DATABASE = "messages.db"


# --------------------------------------------------
# اتصال به دیتابیس
# --------------------------------------------------

def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# --------------------------------------------------
# ساخت دیتابیس
# --------------------------------------------------

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


# --------------------------------------------------
# محافظت از صفحه Admin
# --------------------------------------------------

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):

            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# صفحه اصلی
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# سوال اول
# --------------------------------------------------

@app.route("/questions")
def questions():

    return render_template("questions.html")


# --------------------------------------------------
# سوال دوم
# --------------------------------------------------

@app.route("/question2")
def question2():

    return render_template("question2.html")


# --------------------------------------------------
# صفحه نهایی
# --------------------------------------------------

@app.route("/final")
def final():

    return render_template("final.html")


# --------------------------------------------------
# دریافت پیام
# --------------------------------------------------

@app.route("/send-message", methods=["POST"])
def send_message():

    message = request.form.get("message", "").strip()


    # اگر پیام خالی بود
    if not message:

        return redirect(url_for("final"))


    # اتصال به دیتابیس
    connection = get_db()


    # ذخیره پیام
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


    # بعد از ارسال برگرد به صفحه نهایی
    return render_template(
        "final.html",
        sent=True
    )


# ==================================================
# ADMIN
# ==================================================


# --------------------------------------------------
# صفحه ورود Admin
# --------------------------------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    # اگر قبلاً وارد شده
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


# --------------------------------------------------
# پنل پیام‌ها
# --------------------------------------------------

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


# --------------------------------------------------
# حذف پیام
# --------------------------------------------------

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


# --------------------------------------------------
# خروج از پنل
# --------------------------------------------------

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("admin_login"))


# --------------------------------------------------
# شروع برنامه
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )