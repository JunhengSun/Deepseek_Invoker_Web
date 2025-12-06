from flask import Flask, render_template, redirect, request

app = Flask(__name__)

@app.route("/")
def entry():
    return render_template("entry.html")

@app.route("/create")
def create_chat():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)