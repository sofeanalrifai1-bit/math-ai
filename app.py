from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

DATABASE = "users.db"


# -----------------------
# Database Setup
# -----------------------
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                language TEXT DEFAULT 'no'
            )
        """)
        conn.commit()
        conn.close()

init_db()


# -----------------------
# Home
# -----------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    language = session.get("language", "no")

    explanation = ""
    if request.method == "POST":
        expression = request.form["expression"]

        if language == "no":
            explanation = f"Du skrev: {expression}"
        elif language == "en":
            explanation = f"You wrote: {expression}"
        elif language == "es":
            explanation = f"Escribiste: {expression}"

    return render_template("index.html", explanation=explanation, language=language)


# -----------------------
# Register
# -----------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Username already exists"

    return render_template("register.html")


# -----------------------
# Login
# -----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = user[1]
            session["language"] = user[3]
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


# -----------------------
# Guest Mode
# -----------------------
@app.route("/guest")
def guest():
    session["user"] = "Guest"
    session["language"] = "no"
    return redirect("/")


# -----------------------
# Change Language
# -----------------------
@app.route("/set_language/<lang>")
def set_language(lang):
    session["language"] = lang

    if session.get("user") != "Guest":
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("UPDATE users SET language=? WHERE username=?",
                  (lang, session["user"]))
        conn.commit()
        conn.close()

    return redirect("/")


# -----------------------
# Logout
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
