from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from datetime import datetime

class LeadForm(FlaskForm):
    timestamp = StringField('Timestamp', validators=[DataRequired()])
    label = StringField('Label')
    firstname = StringField('First Name')
    email = StringField('Email')
    phone1 = StringField('Phone1')
    ozip = StringField('OZip')
    dzip = StringField('DZip')
    dcity = StringField('DCity')
    dstate = StringField('DState')
    movesize = StringField('Move Size')
    movedte = StringField('Move DTE')
    conversion = StringField('Conversion')
    validation = StringField('Validation')
    notes = StringField('Notes')
    sent_to_gronat = StringField('Sent to Gronat')
    sent_to_sheets = StringField('Sent to Sheets')
    submit = SubmitField('Submit')

#  to check for duplicate 'POST' requests from the sites
class ProcessedDataForm(FlaskForm):
    data = StringField('Data', validators=[DataRequired()])
    submit = SubmitField('Submit')

#for insert_domain route
class DomainForm(FlaskForm):
    label = StringField('Label')
    domain = StringField('Domain')
    lead_cost = StringField('Lead Cost')
    d_phone_number = StringField('Phone Number')
    send_to_leads_api = IntegerField('Send to Leads API')
    send_to_google_sheet = IntegerField('Send to Google Sheet')
    twilio_number_validation = IntegerField('Twilio Number Validation')
    sms_texting = IntegerField('SMS Texting')
    submit = SubmitField('Submit')