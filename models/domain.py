from app import db 

class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String, nullable=True)
    domain = db.Column(db.String, nullable=True)
    d_phone_number = db.Column(db.String, nullable=True)
    send_to_leads_api = db.Column(db.Integer, nullable=True)
    send_to_google_sheet = db.Column(db.Integer, nullable=True)
    twilio_number_validation = db.Column(db.Integer, nullable=True)
    sms_texting = db.Column(db.Integer, nullable=True)
    lead_cost = db.Column(db.String, nullable=True)
    change_moverref = db.Column(db.Boolean, nullable=True, default=False)
    moverref = db.Column(db.String, nullable=True) 
