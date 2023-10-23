from app import db

class MoverrefConfig(db.Model):
    __tablename__ = 'moverrefconfig'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sequence_order = db.Column(db.Integer, nullable=False)
    repeat_count = db.Column(db.Integer, nullable=False)


#################Shared lead database model
class MoverrefConfig2(db.Model):
    __bind_key__ = 'db2'
    __tablename__ = 'moverrefconfig'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sequence_order = db.Column(db.Integer, nullable=False)
    repeat_count = db.Column(db.Integer, nullable=False)

