from flask import Flask, render_template, request, redirect, session
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey123"

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

@app.route("/clear")
def clear():
    session["chat"] = []
    return redirect("/")

# ================= AI CHAT =================

def ask_ai(message):

    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

    response = requests.post(API_URL, json={
        "inputs": message
    })

    if response.status_code == 200:
        try:
            return response.json()[0]["generated_text"]
        except:
            return "I couldn't process that."
    else:
        return "AI is busy right now. Try again."

# ================= MAIN =================

@app.route("/", methods=["GET", "POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        message = request.form["message"]

        answer = ask_ai(message)

        session["chat"].append({
            "user": message,
            "bot": answer
        })

    return render_template("index.html",
                           chat=session.get("chat", []),
                           user=session["user"])

if __name__ == "__main__":
    app.run(debug=True)
