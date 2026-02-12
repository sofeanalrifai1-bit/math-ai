from flask import Flask, render_template, request, session, redirect, url_for
from sympy import symbols, solve, simplify
from sympy.parsing.sympy_parser import parse_expr

app = Flask(__name__)
app.secret_key = "supersecretkey"

n = symbols('n')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]

        if username.strip() != "":
            session["username"] = username
            session["chat"] = []
            return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def home():

    if "username" not in session:
        return redirect(url_for("login"))

    if "chat" not in session:
        session["chat"] = []

    if request.method == "POST":

        original_input = request.form["expression"]
        user_input = original_input

        try:
            user_input = user_input.replace("^", "**")
            user_input = user_input.replace("x", "*")
            user_input = user_input.replace("X", "*")

            if "=" in user_input:
                left, right = user_input.split("=")
                left_expr = parse_expr(left)
                right_expr = parse_expr(right)

                if left_expr.has(n) or right_expr.has(n):
                    equation = left_expr - right_expr
                    solution = solve(equation, n)

                    if solution:
                        result = f"Løsning: n = {solution[0]}"
                    else:
                        result = "Ingen løsning funnet"
                else:
                    result = f"Svar: {left_expr == right_expr}"
            else:
                expr = parse_expr(user_input)
                simplified = simplify(expr)
                result = f"Svar: {simplified}"

        except:
            result = "Ugyldig uttrykk"

        session["chat"].append({
            "user": original_input,
            "bot": result
        })

        session.modified = True

    return render_template("index.html",
                           chat=session.get("chat", []),
                           username=session["username"])


if __name__ == "__main__":
    app.run(debug=True)
