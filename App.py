from flask import Flask, render_template, redirect, request, session, flash
from Database import Database
from Invoker import Invoker
from datetime import datetime
from typing import Optional
import os
import sqlite3

app = Flask(__name__)
try:    
    app.secret_key = os.getenv("SECRET_KEY")
except Exception as e:
    raise ValueError(f"ERROR: Failed to set secret key: {str(e)}")

def get_database() -> Database:
    return Database("Data.db", "Schema.sql")

def get_invoker(api_key: str, role: Optional[str] = None) -> Invoker:
    return Invoker(api_key, role)

@app.route("/")
def entry():
    return render_template("entry.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        api_key = request.form.get("api_key")
        # username and api_key have been checked in the frontend, so ther're not null
        # check validity of the username
        db = get_database()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,), fetchone=True)
        if not user:
            flash("ERROR: Invalid username")
            return redirect("/login")
        # check validity of the api_key
        invoker = get_invoker(api_key)
        if not invoker.test_api_key_validity():
            flash("ERROR: Invalid API key")
            return redirect("/login")
        # login successfully
        session["logged_in"] = True
        session["user_id"] = user["user_id"]
        session["username"] = username
        session["api_key"] = api_key
        return redirect("/chat")
    elif request.method == "GET":
        if session.get("logged_in", False):
            return redirect("/chat")
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        # username has been checked in the frontend, so it's not null
        # check validity of the username
        db = get_database()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,), fetchone=True)
        if user:
            flash("ERROR: Username already exists")
            return redirect("/register")
        # register successfully
        db.execute("INSERT INTO users (username) VALUES (?)", (username,))
        flash("SUCCESS: Register successfully")
        return redirect("/login")
    elif request.method == "GET":
        return render_template("register.html")
        
@app.route("/chat", methods=["GET"])
def chat():
    if not session.get("logged_in", False):
        flash("ERROR: Please login first")
        return redirect("/login")
    return render_template("menu.html")
    
@app.route("/chat/create", methods=["GET", "POST"])
def create_chat():
    if request.method == "POST":
        # get the paramater form the post
        role = request.form.get("chat_partner")
        temp = float(request.form.get("personality"))
        title = request.form.get("chat_topic")
        # all the parameters have been checked in the frontend, so they're not null
        # create the chat session
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_database()
        db.execute("INSERT INTO chat_sessions (user_id, session_role, session_title, temp, session_created_at) VALUES (?, ?, ?, ?, ?)", (session["user_id"], role, title, temp, created_at))
        session_id = db.execute("SELECT session_id FROM chat_sessions WHERE session_created_at = ?", (created_at,), fetchone=True)["session_id"]
        if not session_id:
            flash("ERROR: Failed to create chat session")
            return redirect("/chat/create")
        session["chat_session_id"] = session_id
        session["chat_session_temp"] = temp
        # create the initial message
        db.execute("INSERT INTO messages (session_id, message_role, message_content, user_id) VALUES (?, ?, ?, ?)", (session_id, "system", role, session["user_id"]))
        flash("SUCCESS: Chat session created successfully")
        return redirect(f"/chat/{session_id}")
    elif request.method == "GET":
        if not session.get("logged_in", False):
            flash("ERROR: Please login first")
            return redirect("/login")
        return render_template("create.html")

@app.route("/chat/<int:session_id>", methods=["GET", "POST"])
def chat_session(session_id):
    if request.method == "POST":
        input_message = request.form.get("message")
        # input_message has been checked in the frontend, so it's not null
        # create the user message
        db = get_database()
        db.execute("INSERT INTO messages (user_id, session_id, message_role, message_content) VALUES (?, ?, ?, ?)", (session["user_id"], session_id, "user", input_message))
        messages = db.execute("SELECT message_role, message_content FROM messages WHERE user_id = ? AND session_id = ? ORDER BY message_id ASC", (session["user_id"], session_id), fetchall=True)
        messages = get_message_list(messages)
        # invoke the API
        invoker = get_invoker(session["api_key"])
        response = invoker.message_invoke(messages, temp=session["chat_session_temp"])
        if "ERROR" in response:
            flash("ERROR: Failed to invoke API")
            return redirect(f"/chat/{session_id}")
        # create the assistant message
        db.execute("INSERT INTO messages (user_id, session_id, message_role, message_content) VALUES (?, ?, ?, ?)", (session["user_id"], session_id, "assistant", response))
        messages = db.execute("SELECT message_role, message_content FROM messages WHERE user_id = ? AND session_id = ? ORDER BY message_id ASC", (session["user_id"], session_id), fetchall=True)
        return render_template("chat.html", messages=messages, username=session["username"], chat_id=session_id)
    elif request.method == "GET":
        if not session.get("logged_in", False):
            flash("ERROR: Please login first")
            return redirect("/login")
        db = get_database()
        messages = db.execute("SELECT message_role, message_content FROM messages WHERE user_id = ? AND session_id = ? ORDER BY message_id ASC", (session["user_id"], session_id), fetchall=True)
        return render_template("chat.html", messages=messages, username=session["username"], chat_id=session_id)

def get_message_list(messages: list[sqlite3.Row]) -> list[dict]:
    '''
        Get the message list from the database
    '''
    message_list = []
    for message in messages:
        message_list.append({"role": message["message_role"], "content": message["message_content"]})
    return message_list

@app.route("/chat/history", methods=["GET"])
def show_history():
    if not session.get("logged_in", False):
        flash("ERROR: Please login first")
        return redirect("/login")
    db = get_database()
    sessions = db.execute("SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY session_created_at DESC", (session["user_id"],), fetchall=True)
    return render_template("history.html", sessions=sessions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)