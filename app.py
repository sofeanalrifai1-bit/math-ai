from flask import Flask, render_template, request, redirect, session
from sympy import symbols, Eq, solve, simplify, expand, factor
from sympy.parsing.sympy_parser import parse_expr
import random

app = Flask(__name__)
app.secret_key = "supersecretkey123"

x = symbols("x")

# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("username")
        session["level"] = "8"
        session["mode"] = "calculator"
        session["chat"] = []
        session["score"] = 0
        return redirect("/")
    return render_template("login.html")


@app.route("/skip")
def skip():
    session["user"] = "Guest"
    session["level"] = "8"
    session["mode"] = "calculator"
    session["chat"] = []
    session["score"] = 0
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= SETTINGS =================

@app.route("/set_mode/<mode>")
def set_mode(mode):
    session["mode"] = mode
    return redirect("/")


@app.route("/set_level/<level>")
def set_level(level):
    session["level"] = level
    return redirect("/")


@app.route("/clear_chat")
def clear_chat():
    session["chat"] = []
    return redirect("/")

# ================= PRACTICE =================

@app.route("/practice")
def practice():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    solution = 2
    question = f"{a}x + {b} = {a*2 + b}"
    session["practice_q"] = question
    session["practice_a"] = solution
    return redirect("/")

# ================= MAIN =================

@app.route("/", methods=["GET", "POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    mode = session.get("mode", "calculator")
    level = session.get("level", "8")

    if request.method == "POST":

        expression = request.form["expression"]
        expression_fixed = expression.replace("^", "**")

        try:
            if mode == "likninger":

                left, right = expression_fixed.split("=")
                eq = Eq(parse_expr(left), parse_expr(right))
                solution = solve(eq, x)

                if level == "8":
                    explanation = f"Move numbers. Isolate x.\nAnswer: x = {solution}"
                elif level == "9":
                    explanation = f"Subtract terms and divide.\nSolution: x = {solution}"
                else:
                    explanation = f"Solve algebraically.\nSolution: x = {solution}"

            elif mode == "algebra":

                expr = parse_expr(expression_fixed)
                explanation = f"""
Simplified: {simplify(expr)}
Expanded: {expand(expr)}
Factored: {factor(expr)}
"""

            elif mode == "brok":

                expr = parse_expr(expression_fixed)
                explanation = f"Fraction simplified: {simplify(expr)}"

            else:

                expr = parse_expr(expression_fixed)
                explanation = f"Result: {simplify(expr)}"

        except:
            explanation = "Invalid mathematical expression."

        session["chat"].append({
            "user": expression,
            "bot": explanation
        })

    return render_template(
        "index.html",
        chat=session.get("chat", []),
        user=session["user"],
        mode=mode,
        level=level,
        score=session.get("score", 0),
        practice_q=session.get("practice_q")
    )

if __name__ == "__main__":
    app.run(debug=True)
