from app import db

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=True)
    firstname = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    phone1 = db.Column(db.String, nullable=True)
    ozip = db.Column(db.String, nullable=True)
    dzip = db.Column(db.String, nullable=True)
    dcity = db.Column(db.String, nullable=True)
    dstate = db.Column(db.String, nullable=True)
    movesize = db.Column(db.String, nullable=True)
    movedte = db.Column(db.String, nullable=True)
    conversion = db.Column(db.String, nullable=True)
    validation = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)
    sent_to_gronat = db.Column(db.String, nullable=True)
    sent_to_sheets = db.Column(db.String, nullable=True)
    moverref = db.Column(db.String, nullable=True)


######################Shared Lead database model
class Lead2(db.Model):
    __bind_key__ = 'db2'
    __tablename__ = 'lead'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=True)
    firstname = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    phone1 = db.Column(db.String, nullable=True)
    ozip = db.Column(db.String, nullable=True)
    dzip = db.Column(db.String, nullable=True)
    dcity = db.Column(db.String, nullable=True)
    dstate = db.Column(db.String, nullable=True)
    movesize = db.Column(db.String, nullable=True)
    movedte = db.Column(db.String, nullable=True)
    conversion = db.Column(db.String, nullable=True)
    validation = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)
    sent_to_gronat = db.Column(db.String, nullable=True)
    sent_to_sheets = db.Column(db.String, nullable=True)
    moverref = db.Column(db.String, nullable=True)