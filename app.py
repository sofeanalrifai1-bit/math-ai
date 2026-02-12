from flask import Flask, render_template, request
from sympy import symbols, Eq, solve, sympify

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    solution = None
    steps = None

    if request.method == "POST":
        problem = request.form["problem"]
        x = symbols('x')

        try:
            left, right = problem.split("=")
            equation = Eq(sympify(left), sympify(right))
            solution_value = solve(equation, x)

            solution = solution_value
            steps = f"""
Step 1: Start with the equation:
{problem}

Step 2: Move terms to isolate x

Step 3: Solve for x

Final Answer: x = {solution_value}
"""
        except:
            solution = "Invalid input. Try format like 2*x+5=15"

    return render_template("index.html", solution=solution, steps=steps)

if __name__ == "__main__":
    app.run(debug=True)
