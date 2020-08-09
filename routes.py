from app import app
from flask import render_template, request, redirect
from db import db
import comments, users

@app.route("/deck/<int:id>/comments")
def index(id):
    list = comments.get_list(id)
    return render_template("comments.html", deck_id=id, count=len(list), comments=list)

@app.route("/")
def first():
    sql = "SELECT id, topic FROM decks ORDER BY id DESC"
    result = db.session.execute(sql)
    decks = result.fetchall()
    return render_template("first.html", decks=decks)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/create", methods=["POST"])
def create():
    topic = request.form["topic"]
    description = request.form["description"]
    hashtags = request.form["hashtags"]
    sql = "INSERT INTO decks (topic, description, hashtags, created_at) VALUES (:topic, :description, :hashtags, NOW()) RETURNING id"
    result = db.session.execute(sql, {"topic":topic, "description":description, "hashtags":hashtags})
    deck_id = result.fetchone()[0]
    word = request.form["word"]
    sql = "INSERT INTO frontside (deck_id, word) VALUES (:deck_id, :word) RETURNING id"
    result2 = db.session.execute(sql, {"deck_id":deck_id, "word":word})
    frontside_id = result2.fetchone()[0]
    answer = request.form["answer"]
    sql = "INSERT INTO backside (frontside_id, answer) VALUES (:frontside_id, :answer) RETURNING id"
    result = db.session.execute(sql, {"frontside_id":frontside_id, "answer":answer})
    db.session.commit()
    return redirect("/new")

@app.route("/addcards")
def addcards():
    return render_template("addcards.html")

@app.route("/added", methods=["POST"])
def added():
    deck_id = 9
    word = request.form["word"]
    sql = "INSERT INTO frontside (deck_id, word) VALUES (:deck_id, :word) RETURNING id"
    result = db.session.execute(sql, {"deck_id":deck_id, "word":word})
    frontside_id = result.fetchone()[0]
    answer = request.form["answer"]
    sql = "INSERT INTO backside (frontside_id, answer) VALUES (:frontside_id, :answer) RETURNING id"
    result = db.session.execute(sql, {"frontside_id":frontside_id, "answer":answer})
    db.session.commit()
    return redirect("/addcards")

@app.route("/deck/<int:id>")
def deck(id):
    sql = "SELECT topic FROM decks WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    topic = result.fetchone()[0]
    sql = "SELECT id, word FROM frontside WHERE deck_id=:id"
    result = db.session.execute(sql, {"id":id})
    frontside = result.fetchone()
    word = frontside[1]
    frontside_id = frontside[0]
    return render_template("frontside.html", deck_id=id, frontside_id=frontside_id, topic=topic, word=word)

@app.route("/answer/<int:deck_id>/<int:frontside_id>")
def answer(deck_id, frontside_id):
    sql = "SELECT topic FROM decks WHERE id=:id"
    result = db.session.execute(sql, {"id":deck_id})
    topic = result.fetchone()[0]
    sql = "SELECT id, answer FROM backside WHERE frontside_id=:id"
    result = db.session.execute(sql, {"id":frontside_id})
    answer = result.fetchone()[1]
    return render_template("backside.html", topic=topic, answer=answer)

@app.route("/deck/<int:id>/newcomment")
def newcomment(id):
    return render_template("newcomment.html", deck_id=id)

@app.route("/deck/<int:id>/send", methods=["post"])
def send(id):
    content = request.form["content"]
    if comments.send(content, id):
        return redirect("/deck/"+str(id)+"/comments")
    else:
        return render_template("error.html",message="The comment could not be sent")

@app.route("/login", methods=["get","post"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username,password):
            return redirect("/")
        else:
            return render_template("error.html",message="Wrong username or password.")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["get","post"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.register(username,password):
            return redirect("/")
        else:
            return render_template("error.html",message="Could not register.")