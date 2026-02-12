from flask import Flask, render_template, request, redirect, session
from sympy import symbols, Eq, solve, simplify, expand, factor
from sympy.parsing.sympy_parser import parse_expr

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# =========================
# LOGIN PAGE
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        session["user"] = username
        return redirect("/")
    return render_template("login.html")


@app.route("/skip")
def skip():
    session["user"] = "Guest"
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# MODE SWITCH
# =========================

@app.route("/set_mode/<mode>")
def set_mode(mode):
    session["mode"] = mode
    return redirect("/")


# =========================
# CLEAR CHAT
# =========================

@app.route("/clear_chat")
def clear_chat():
    session["chat"] = []
    return redirect("/")


# =========================
# MAIN PAGE
# =========================

@app.route("/", methods=["GET", "POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    if "mode" not in session:
        session["mode"] = "calculator"

    if "chat" not in session:
        session["chat"] = []

    mode = session["mode"]

    if request.method == "POST":

        expression = request.form["expression"]

        try:
            x = symbols('x')

            # Fix 2x -> 2*x
            expression_fixed = expression.replace("^", "**")

            if mode == "likninger":

                if "=" not in expression_fixed:
                    explanation = "⚠️ You must include = in equation"
                else:
                    left, right = expression_fixed.split("=")
                    eq = Eq(parse_expr(left), parse_expr(right))
                    solution = solve(eq, x)
                    explanation = f"""
Step 1: Move terms
Step 2: Solve equation
Solution:
x = {solution}
"""

            elif mode == "algebra":

                expr = parse_expr(expression_fixed)
                explanation = f"""
Simplified:
{simplify(expr)}

Expanded:
{expand(expr)}

Factored:
{factor(expr)}
"""

            elif mode == "brok":

                expr = parse_expr(expression_fixed)
                explanation = f"""
Fraction simplified:
{simplify(expr)}
"""

            else:  # calculator

                expr = parse_expr(expression_fixed)
                explanation = f"""
Result:
{simplify(expr)}
"""

        except Exception as e:
            explanation = "❌ Invalid mathematical expression"

        session["chat"].append({
            "user": expression,
            "bot": explanation
        })

    return render_template("index.html",
                           chat=session["chat"],
                           mode=mode,
                           user=session["user"])


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
