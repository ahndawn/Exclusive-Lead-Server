#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import jsonify
from urllib.parse import unquote
from googleapiclient.discovery import build
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from twilio.rest import Client
from google.oauth2 import service_account
import pytz
import json
import os


# Access the environment variables
database_url = os.environ.get('DATABASE_URL')
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(twilio_account_sid, twilio_auth_token)


###########################    format date
def format_move_date(movedate):
    try:
        # Try to parse the input date string as MM/DD/YYYY format
        date_obj = datetime.strptime(movedate, '%m/%d/%Y')
        # If parsing is successful, return the input date as is
        return movedate
    except ValueError:
        try:
            # Try to parse the input date string as YYYY-MM-DD format
            date_obj = datetime.strptime(movedate, '%Y-%m-%d')
            # Format the datetime object as MM/DD/YYYY
            formatted_date = date_obj.strftime('%m/%d/%Y')
            return formatted_date
        except ValueError:
            # If the date_string is not in either format, return an empty string or handle the error as needed
            return ''
        
#format phone
#################################################################
def format_phone_number(phone_number):
    # Remove all non-numeric characters
    phone_number = ''.join(filter(str.isdigit, phone_number))

    # Check if phone number has the correct length for international format
    if len(phone_number) < 10 or len(phone_number) > 12:
        return 'Invalid phone number'

    # Return the phone number without any dashes
    if len(phone_number) == 10:  # US number without country code
        return f'{phone_number[:3]}{phone_number[3:6]}{phone_number[6:]}'
    elif len(phone_number) == 11:  # International number with 1 digit country code
        return f'{phone_number[:1]}{phone_number[1:4]}{phone_number[4:7]}{phone_number[7:]}'
    elif len(phone_number) == 12:  # International number with 2 digits country code
        return f'{phone_number[:2]}{phone_number[2:5]}{phone_number[5:8]}{phone_number[8:]}'
##################################################################
# Google Sheets API credentials
google_sheets_credentials = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
creds = None
if google_sheets_credentials:
    creds_data = json.loads(google_sheets_credentials)
    creds = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
    )

##########################################################
    # Function to send a Twilio message
def send_message(first_name, phone_number):
    now = datetime.now()
    hour = now.hour  # 24-hour format

    if 8 <= hour < 23:  # between 8AM and 11:15PM
        body = f"Hey {first_name}, your moving estimate is ready! Please Call (561) 565-6050"
    else:  # between 11:15PM and 8AM
        body = "Our Agents are currently out of the office. Please Call (561) 565-6050 8am-11pm EST"

    try:
        message = client.messages.create(
            to=phone_number,
            # from_="15614851468", 
            from_="8883053791", 
            body=body
        )
        print("Message sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send message: {e}")
        return False
    

###################################################################
# Push the data to the corresponding Google Sheet by Label name 
spreadsheet_ids_and_ranges = {
    'Spot Tower': {'spreadsheet_id': '1d4lIy0a_slZKYKx3BRM1i57pWX7SIMFllWC6pNrYlXQ', 'range': 'Sheet1!A2'},
    'Savvy': {'spreadsheet_id': '1ZQ7wNiKNmH4x-10Tl2s0dgqDr8t7FiyIVpNNUk006QU', 'range': 'Sheet1!A2'},
    'Crispx': {'spreadsheet_id': '17qSaCVHHrMiRKd6Q11_rq-AQ07isulU-TxKkyvefoeI', 'range': 'Leadpost!A2'},
    'ConAds': {'spreadsheet_id': '1LlNqoLEijBcpITbXOE_UlNeH0of9QuKReA6S6fPszI4', 'range': 'Sheet1!A2'},
    'IQ Media': {'spreadsheet_id': '1RUYZ9aONYGEq26POCF0JGNjiZ1GsBzRHIs1h3BbZq5A', 'range': 'Sheet1!A2'},
    'Top10': {'spreadsheet_id': '12uCFTYzn9WydVZInVaZpTZKg7N3Rz65x4rsbjjqnIAk', 'range': 'LeadFlow!A2'},
    'ConAdsP1': {'spreadsheet_id': '1UpcqT5qzqNv7u1e0Q-DY7mqke6sqYm5WM_Qdr6rDGJ4', 'range': 'Sheet1!A2'},
}


##################################################################
# LEAD INSERTION
def insert_data_into_db(data, sent_to_gronat, sent_to_sheets, validation):
    from app import db
    from models.lead import Lead
    try:
        # Check for duplicate data
        existing_data = Lead.query.filter_by(
            firstname=data.get('firstname'),
            email=data.get('email'),
            phone1=data.get('phone1')
        ).first()
        if existing_data:
            print('Existing data, skipping...')
            return jsonify({"message": "Duplicate data found in the database. Skipping insertion."}), 201
        
        # if form post request has start/end state/city or not
        dcity = data.get('dcity', '')
        dstate = data.get('dstate', '')
        dzip = data.get('dzip', '')
        # Validate ref_no, it must not be an empty string
        ref_no = data.get('ref_no')
        if not ref_no or ref_no.strip() == '':
            print("Invalid ref_no, ref_no cannot be an empty string.")
            return jsonify({"message": "Invalid ref_no. ref_no cannot be an empty string."}), 400
        ref_no = unquote(ref_no)
        
        timezone = pytz.timezone('America/New_York')
        current_datetime = datetime.now(timezone)
        timestamp = current_datetime.strftime('%Y-%m-%d')
        
        # Insert the data into the database
        lead = Lead(
            label=data.get('label'),
            timestamp=timestamp,
            firstname=data.get('firstname'),
            email=data.get('email'),
            phone1=data.get('phone1'),
            ozip=data.get('ozip'),
            dzip=dzip,
            dcity=dcity,
            dstate=dstate,
            movesize=data.get('movesize'),
            movedte=data.get('movedte'),
            conversion=ref_no,
            validation=validation,
            notes=json.dumps(data.get('notes', {})),
            sent_to_gronat=sent_to_gronat,
            sent_to_sheets=sent_to_sheets
        )
        
        db.session.add(lead)
        db.session.commit()

        print('added successfully to Heroku')
        return True  # Return True if insertion was successful
    
    except IntegrityError:
        db.session.rollback()
        print('Error: Duplicate data in lead table.')
    except Exception as e:
        print(f"Failed to insert data into the database: {e}")
        return False  # Return False if insertion failed.

