from app import app
from flask import render_template, request, redirect
from db import db
import comments, users

@app.route("/")
def index():
    lines = ["Study", "with flashcards", "and have fun!"]
    return render_template("index.html", items=lines)

@app.route("/deck/<int:id>/comments")
def comment(id):
    list = comments.get_list(id)
    return render_template("comments.html", deck_id=id, count=len(list), comments=list)

@app.route("/information")
def information():
    return render_template("information.html")

@app.route("/first")
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
    answer = request.form["answer"]
    sql = "INSERT INTO frontside (deck_id, word, answer) VALUES (:deck_id, :word, :answer) RETURNING id"
    result2 = db.session.execute(sql, {"deck_id":deck_id, "word":word, "answer":answer})
    db.session.commit()
    return redirect("/first")

@app.route("/addcards/<int:id>")
def addcards(id):
    sql = "SELECT topic FROM decks WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    topic = result.fetchone()[0]
    return render_template("addcards.html", deck_id=id, topic=topic)

@app.route("/added/<int:deck_id>", methods=["POST"])
def added(deck_id):
    word = request.form["word"]
    answer = request.form["answer"]
    sql = "INSERT INTO frontside (deck_id, word, answer) VALUES (:deck_id, :word, :answer) RETURNING id"
    result = db.session.execute(sql, {"deck_id":deck_id, "word":word, "answer":answer})
    db.session.commit()
    return redirect("/addcards/" + str(deck_id))

@app.route("/deck/<int:id>")
def deck(id):
    sql = "SELECT topic FROM decks WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    topic = result.fetchone()[0]
    sql = "SELECT id, word FROM frontside WHERE deck_id=:id ORDER BY RANDOM() LIMIT 1"
    result = db.session.execute(sql, {"id":id})
    frontside = result.fetchone()
    word = frontside[1]
    frontside_id = frontside[0]
    return render_template("frontside.html", deck_id=id, frontside_id=frontside_id, topic=topic, word=word)

@app.route("/answer/<int:deck_id>/<int:frontside_id>")
def answer(deck_id, frontside_id):
    user_id = users.user_id()
    sql = "SELECT topic FROM decks WHERE id=:id"
    result = db.session.execute(sql, {"id":deck_id})
    topic = result.fetchone()[0]
    sql = "SELECT id, answer FROM frontside WHERE id=:id"
    result = db.session.execute(sql, {"id":frontside_id})
    answer = result.fetchone()[1]
    sql = "SELECT COUNT(*) FROM hard WHERE frontside_id=:frontside_id AND user_id=:user_id"
    result = db.session.execute(sql, {"frontside_id":frontside_id, "user_id":user_id})
    is_hard = result.fetchone()[0] > 0
    return render_template("backside.html", topic=topic, answer=answer, deck_id=deck_id, frontside_id=frontside_id, is_hard=is_hard)

@app.route("/test/<int:deck_id>")
def test(deck_id):
    sql = "SELECT topic FROM decks WHERE id=:id"
    result = db.session.execute(sql, {"id":deck_id})
    topic = result.fetchone()[0]
    sql = "SELECT id, word FROM frontside WHERE deck_id=:id ORDER BY RANDOM() LIMIT 1"
    result = db.session.execute(sql, {"id":deck_id})
    frontside = result.fetchone()
    word = frontside[1]
    frontside_id = frontside[0]
    return render_template("test.html", topic=topic, word=word, deck_id=deck_id, frontside_id=frontside_id)

@app.route("/testcheck/<int:deck_id>/<int:frontside_id>", methods=["POST"])
def testcheck(deck_id, frontside_id):
    sql = "SELECT id, answer FROM frontside WHERE id=:id"
    result = db.session.execute(sql, {"id":frontside_id})
    answer = result.fetchone()[1]
    userinput = request.form["answer"]
    if userinput == answer:
        return render_template("correct.html", deck_id=deck_id)
    else:
        return render_template("wrong.html", deck_id=deck_id)

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
            return redirect("/first")
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

@app.route("/hard/<int:frontside_id>", methods=["post"])
def hard(frontside_id):
    user_id = users.user_id()
    sql= "INSERT INTO hard (user_id, frontside_id) VALUES (:user_id, :frontside_id)"
    result = db.session.execute(sql, {"user_id":user_id, "frontside_id":frontside_id})
    db.session.commit()
    return redirect(request.referrer)

@app.route("/unhard/<int:frontside_id>", methods=["post"])
def unhard(frontside_id):
    user_id = users.user_id()
    sql="DELETE FROM hard WHERE user_id=:user_id AND frontside_id=:frontside_id"
    result = db.session.execute(sql, {"user_id":user_id, "frontside_id":frontside_id})
    db.session.commit()
    return redirect(request.referrer)