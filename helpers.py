#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import jsonify
from urllib.parse import unquote
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from twilio.rest import Client
from google.oauth2 import service_account
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode
from googleapiclient.errors import HttpError
import smtplib
import pytz
import json
import os
import requests


# Access the environment variables
database_url = os.environ.get('DATABASE_URL')
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(twilio_account_sid, twilio_auth_token)

########################### Send email
def send_email(label,dzip,dcity,dstate,ref_no, email, data, movedte, ozip, phone_number, first_name, icid):
    # Construct the email message
    subject = f"New {str(label)} Lead"
    from_email = "quoteform@safeship-moving.com"
    to_email = "admin@safeshipmoving.com, ahni@safeshipmoving.com"
     # Determine the destination value
    destination = dzip if dzip else f'{dcity}, {dstate}'

    if label == 'Crispx':
        indicator = f'GCLID {ref_no}\n                       ICID: {icid}'
    else:
        indicator = f'ICID {icid}'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Format the email body
    email_body = f"""
        <{email}>
        Name: {first_name}
        Phone: {phone_number}
        Pickup Zip: {ozip}
        Destination: {destination}
        Move Size: {data.get('movesize')}
        Move Date: {movedte}
        Notes: {indicator}
        Conversion ID: (ref_no) {ref_no}
        Conversion Time: {datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')}
    """
    msg.attach(MIMEText(email_body, 'plain'))

    # Send the email
    try:
        with smtplib.SMTP('smtp-relay.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login('chris@safeshipmoving.com', 'xayfbkehwpiwujly')
            server.sendmail(from_email, to_email.split(','), msg.as_string())
            print("SUCCESS: Email")
    except Exception as e:
        print(f"FAILED to send email: {e}")
###########################    format date
def format_move_date(movedate):
    formats = ['%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y.%m.%d', '%d%m%y']
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(movedate, fmt)
            # Once a correct format is found, format the datetime object as MM/DD/YYYY and return
            formatted_date = date_obj.strftime('%m/%d/%Y')
            return formatted_date
        except ValueError:
            # If the current format doesn't match, continuFe to the next format
            continue
    
    # If no formats matched, return the original movedate
    return movedate


#############################
def calculate_volume(movesize):
    volume_mapping = {
        'Studio': 450,
        '1 Bedroom': 650,
        '2 Bedrooms': 900,
        '3 Bedrooms': 1200,
        '4 Bedrooms': 1500,
        '5+ Bedrooms': 1800,
        'Office': 1000
    }
    return volume_mapping.get(movesize, 0)


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
        print("SUCCESS: Text Sent")
        return True
    except Exception as e:
        print(f"FAILED to send message: {e}")
        return False
    

###################################################################
# Push the data to the corresponding Google Sheet by Label name 
spreadsheet_ids_and_ranges = {
    'Spot Tower': {'spreadsheet_id': '1d4lIy0a_slZKYKx3BRM1i57pWX7SIMFllWC6pNrYlXQ', 'range': 'Sheet1!A2'},
    'Special EX': {'spreadsheet_id': '1d4lIy0a_slZKYKx3BRM1i57pWX7SIMFllWC6pNrYlXQ', 'range': 'Sheet1!A2'},
    'Savvy': {'spreadsheet_id': '1ZQ7wNiKNmH4x-10Tl2s0dgqDr8t7FiyIVpNNUk006QU', 'range': 'Sheet1!A2'},
    'Crispx': {'spreadsheet_id': '17qSaCVHHrMiRKd6Q11_rq-AQ07isulU-TxKkyvefoeI', 'range': 'Leadpost!A2'},
    'ConAds': {'spreadsheet_id': '1LlNqoLEijBcpITbXOE_UlNeH0of9QuKReA6S6fPszI4', 'range': 'Sheet1!A2'},
    'IQ Media': {'spreadsheet_id': '1RUYZ9aONYGEq26POCF0JGNjiZ1GsBzRHIs1h3BbZq5A', 'range': 'Sheet1!A2'},
    'Interstate EX': {'spreadsheet_id': '1RUYZ9aONYGEq26POCF0JGNjiZ1GsBzRHIs1h3BbZq5A', 'range': 'Sheet2!A2'},
    'Top10': {'spreadsheet_id': '12uCFTYzn9WydVZInVaZpTZKg7N3Rz65x4rsbjjqnIAk', 'range': 'LeadFlow!A2'},
    'ConAdsP1': {'spreadsheet_id': '1UpcqT5qzqNv7u1e0Q-DY7mqke6sqYm5WM_Qdr6rDGJ4', 'range': 'Sheet1!A2'},
    'ConAds EX': {'spreadsheet_id': '1UpcqT5qzqNv7u1e0Q-DY7mqke6sqYm5WM_Qdr6rDGJ4', 'range': 'Sheet2!A2'},
}

##################################################################
# LEAD INSERTION
def insert_data_into_db(data, sent_to_gronat, sent_to_sheets, validation, movesize, movedte, icid):
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
            movesize=movesize,
            movedte=movedte,
            conversion=ref_no,
            validation=validation,
            notes=icid,
            sent_to_gronat=sent_to_gronat,
            sent_to_sheets=sent_to_sheets
        )
        
        db.session.add(lead)
        db.session.commit()

        print('SUCCESSFUL POST: Heroku')
        return True  # Return True if insertion was successful
    
    except IntegrityError:
        db.session.rollback()
        print('Error: Duplicate data in lead table.')
    except Exception as e:
        print(f"FAILED to insert data into the database: {e}")
        return False  # Return False if insertion failed.
    

#####################################
 # Prepare data for Gronat POST request
def send_to_gronat(label, moverref, first_name, email, phone_number, ozip, dzip, dcity, dstate, data, movedte, send_to_leads_api, icid):
    if movedte == '':
        movedte = (datetime.today() + timedelta(days=30)).strftime('%m %d %Y')
    api_url = "https://lead.hellomoving.com/LEADSGWHTTP.lidgw?&API_ID=5E3FD536C2D6"
    query_string = urlencode({
        'label': label,
        'moverref': moverref,
        'firstname': first_name,
        'email': email,
        'phone1': phone_number,
        'ozip': ozip,
        'dzip': dzip,
        'dcity': dcity,
        'dstate': dstate,
        'movesize': data.get('movesize'),
        'movedte': movedte,
        'notes': 'ICID: ' + icid,
        'volume': calculate_volume(data.get('movesize'))
    })

    # check domain setting (1 = checked box in settings)
    if send_to_leads_api == 1:
        response = requests.post(api_url, data=query_string)
        if response.status_code >= 200 and response.status_code < 300 and 'OK' in response.text:
            print(f"GRONAT POST SUCCESS: {response.status_code}, Response message: {response.text}")
            return True
        else:
            print(f"GRONAT POST FAILED: {response.status_code}, Response message: {response.text}")
            return False



############################# send to google sheets
def send_to_sheets(timestamp,first_name,ozip,dzip,dcity,dstate,data,ref_no,validation,label, phone_number,lead_cost, icid):
    spreadsheet_config = spreadsheet_ids_and_ranges.get(label)
    if spreadsheet_config:
        values_to_append = [
            timestamp,
            first_name,
            ozip,
            dzip,
            dcity,
            dstate,
            data.get('movesize'),
            data.get('movedte'),
            ref_no,
            validation,
            icid
        ]
        # Append phone_number and lead_cost together for specific labels
        if label in ['IQ Media', 'Spot Tower', 'Top10', 'ConAdsP1', 'ConAds EX', 'Interstate EX', 'Special EX']:
            values_to_append.extend([phone_number, str(lead_cost)])
        else:
            values_to_append.append(str(lead_cost))   

        body = {'values': [values_to_append]}
        # check domain setting (1 = checked box in settings)
        try:
            service = build('sheets', 'v4', credentials=creds)
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_config['spreadsheet_id'],
                range=spreadsheet_config['range'],
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()  
            print('SUCCESS: Google Sheets')
            return True
        except HttpError as error: 
            print('FAILED POST to Google Sheets: ', error._get_reason())
            return False