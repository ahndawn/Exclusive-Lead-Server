from app import db 

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    moverref_count = db.Column(db.Integer, default=0)