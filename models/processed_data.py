from app import db

class ProcessedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String, unique=True, nullable=False)