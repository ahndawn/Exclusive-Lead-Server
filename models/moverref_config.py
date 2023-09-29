from app import db

class MoverrefConfig(db.Model):
    __tablename__ = 'moverrefconfig'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sequence_order = db.Column(db.Integer, nullable=False)
    repeat_count = db.Column(db.Integer, nullable=False)

class SecondModel(db.Model):
    __bind_key__ = 'second_db'
    __tablename__ = 'moverrefconfig'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sequence_order = db.Column(db.Integer, nullable=False)
    repeat_count = db.Column(db.Integer, nullable=False)

