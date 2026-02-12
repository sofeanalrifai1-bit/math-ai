from flask import Flask, render_template, request, redirect, session
import sqlite3
from sympy import symbols, Eq, solve, simplify
from sympy.parsing.sympy_parser import parse_expr

app = Flask(__name__)
app.secret_key = "supersecretkey123"

x = symbols("x")

# ========== DATABASE SETUP ==========

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ========== LANGUAGE SYSTEM ==========

translations = {
    "en": {
        "welcome": "Welcome",
        "placeholder": "Type your math problem...",
        "clear": "Clear Chat",
        "logout": "Logout"
    },
    "no": {
        "welcome": "Velkommen",
        "placeholder": "Skriv matteoppgave...",
        "clear": "Tøm Chat",
        "logout": "Logg ut"
    }
}

def t(key):
    lang = session.get("lang", "en")
    return translations[lang][key]

@app.route("/set_language/<lang>")
def set_language(lang):
    session["lang"] = lang
    return redirect("/")

# ========== AUTH ==========

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username,password) VALUES (?,?)",
                      (username,password))
            conn.commit()
        except:
            conn.close()
            return "User already exists"
        conn.close()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            session["chat"] = []
            session["lang"] = "en"
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/clear")
def clear():
    session["chat"] = []
    return redirect("/")

# ========== SMART MATH SOLVER ==========

def solve_math(expression):

    expression = expression.replace("^","**")

    try:
        if "=" in expression:
            left,right = expression.split("=")
            eq = Eq(parse_expr(left), parse_expr(right))
            solution = solve(eq,x)

            explanation = f"""
Step 1: Move all terms to one side.
Step 2: Solve equation.
Solution: x = {solution}
"""
            return explanation

        else:
            result = simplify(parse_expr(expression))

            explanation = f"""
Step 1: Simplify the expression.
Step 2: Combine like terms.
Result: {result}
"""
            return explanation

    except:
        return "I could not understand the math problem."

# ========== MAIN ==========

@app.route("/", methods=["GET","POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        expression = request.form["expression"]
        answer = solve_math(expression)

        session["chat"].append({
            "user": expression,
            "bot": answer
        })

    return render_template("index.html",
                           chat=session.get("chat",[]),
                           user=session["user"],
                           t=t)

if __name__ == "__main__":
    app.run(debug=True)
