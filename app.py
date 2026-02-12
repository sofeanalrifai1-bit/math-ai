from flask import Flask, render_template, request, redirect, session
from sympy import symbols, Eq, solve, simplify
from sympy.parsing.sympy_parser import parse_expr

app = Flask(__name__)
app.secret_key = "supersecretkey123"

x = symbols("x")

# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("username")
        session["chat"] = []
        return redirect("/")
    return render_template("login.html")


@app.route("/skip")
def skip():
    session["user"] = "Guest"
    session["chat"] = []
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= MAIN =================

@app.route("/", methods=["GET", "POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        expression = request.form["expression"]
        expression_fixed = expression.replace("^", "**")

        try:
            if "=" in expression_fixed:
                left, right = expression_fixed.split("=")
                eq = Eq(parse_expr(left), parse_expr(right))
                solution = solve(eq, x)
                answer = f"The solution is x equals {solution}"
            else:
                result = simplify(parse_expr(expression_fixed))
                answer = f"The answer is {result}"
        except:
            answer = "I could not understand that math problem."

        session["chat"].append({
            "user": expression,
            "bot": answer
        })

    return render_template("index.html",
                           chat=session.get("chat", []),
                           user=session["user"])

if __name__ == "__main__":
    app.run(debug=True)
