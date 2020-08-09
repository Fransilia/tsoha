from db import db
import users

def get_list(deck_id):
    sql = "SELECT C.content, U.username, C.sent_at FROM comments C, users U WHERE C.user_id=U.id AND C.deck_id=:deck_id ORDER BY C.id"
    result = db.session.execute(sql, {"deck_id":deck_id})
    return result.fetchall()

def send(content, deck_id):
    user_id = users.user_id()
    if user_id == 0:
        return False
    sql = "INSERT INTO comments (content, user_id, sent_at, deck_id) VALUES (:content, :user_id, NOW(), :deck_id)"
    db.session.execute(sql, {"content":content, "user_id":user_id, "deck_id":deck_id})
    db.session.commit()
    return True