#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template, session
from sqlalchemy.exc import IntegrityError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask_login import current_user
from urllib.parse import urlencode, unquote
from helpers import client, send_message, creds, spreadsheet_ids_and_ranges, format_phone_number
from datetime import datetime
import pytz
import json
import requests


app_bp = Blueprint('app', __name__)

@app_bp.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', current_user=current_user)
    

@app_bp.route('/', methods=['GET', 'POST'])
def add_data():
    from app import db
    from models.domain import Domain
    from models.processed_data import ProcessedData
    from helpers import insert_data_into_db
    if request.method == 'POST':
        data = request.get_json()
        print(f"Received data: {data}")

        # if form post request has start/end state/city or not
        ozip = data.get('ozip', '')
        dcity = data.get('dcity', '')
        dstate = data.get('dstate', '')
        dzip = data.get('dzip', '')
        email = data.get('email')
        label = data.get('label')
        phnumber = data.get('phone1')
        phone_number = format_phone_number(phnumber)
        first_name = data.get('firstname')
        # Validate ref_no, it must not be an empty string
        ref_no = data.get('ref_no')
        if not ref_no or ref_no.strip() == '':
            print("Invalid ref_no, ref_no cannot be an empty string.")
            return jsonify({"message": "Invalid ref_no. ref_no cannot be an empty string."}), 400
        ref_no = unquote(ref_no)
        if not email or not phone_number or not first_name:
            print("PHONE, EMAIL, AND NAME ARE REQUIRED. SKIPPING INSERTION")
            return jsonify({"message": "Email, phone number, and name are required."}), 400 

        # Fetch domain settings from the database. 1 means the checkbox is 'checked' for domain settings and makes the value true for the specific setting, 0 is false
        domain_settings = Domain.query.filter_by(label=label).first()

        if not domain_settings:
            #automatically turn on all settings if label of a domain is not found in database
            print(f"No domain settings found for label: {label}")
            send_to_leads_api = 1
            send_to_google_sheet = 1
            twilio_number_validation = 1
            sms_texting = 1
        else:
            #if label of domain is found in database, use settings specified for that domain 
            send_to_leads_api = domain_settings.send_to_leads_api
            send_to_google_sheet = domain_settings.send_to_google_sheet
            twilio_number_validation = domain_settings.twilio_number_validation
            sms_texting = domain_settings.sms_texting

        # Prepare data for Gronat POST request
        sent_to_gronat = '0'
        api_url = "https://lead.hellomoving.com/LEADSGWHTTP.lidgw?&API_ID=5E3FD536C2D6"
        query_string = urlencode({
            'label': label,
            'moverref': data.get('moverref'),
            'firstname': first_name,
            'email': email,
            'phone1': phone_number,
            'ozip': ozip,
            'dzip': dzip,
            'dcity': dcity,
            'dstate': dstate,
            'movesize': data.get('movesize'),
            'movedte': data.get('movedte'),
            'notes': 'ICID: ' + data.get('notes'),
        })

        # check domain setting (1 = checked box in settings)
        if send_to_leads_api == 1:
            response = requests.post(api_url, data=query_string)
            if response.status_code >= 200 and response.status_code < 300:
                print("Sent to Gronat")
                print(f"Response code: {response.status_code}, Response message: {response.text}")
                sent_to_gronat = '1'
            else:
                print("Gronat posting failed")
                print(f"Response code: {response.status_code}, Response message: {response.text}")


        # default value if validation is not ran '-1'
        validation = '-1'
        # check domain setting (1 = checked box in settings)
        if twilio_number_validation == 1:
            try:
                number = client.lookups.phone_numbers(phone_number).fetch(country_code='US')
                # change value in table to '1' if number is valid
                validation = '1'
                print(f"Phone number is valid: {phone_number}")
            except Exception as e:
                print(f"Phone number is invalid: {phone_number}")
                # change value in table to '0' if number is invalid
                validation = '0'
            if sms_texting == 1 and validation == '1':
                success = send_message(first_name, phone_number)
                if not success:
                    print(f"Failed to send sms to {phone_number}")


        timezone = pytz.timezone('America/New_York')
        current_datetime = datetime.now(timezone)
        timestamp = current_datetime.strftime('%Y-%m-%d')
        

        # default value '0' if not sent to sheet, '1' if sent. use spreadsheet_config dictionary
        spreadsheet_config = spreadsheet_ids_and_ranges.get(label)
        sent_to_sheets = '0'
        if spreadsheet_config:
            body = {
                'values': [[
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
                    data.get('notes')
                ]]
            }
            if label == 'IQ Media' or 'Spot Tower':
                body['values'][0].append(phone_number)
            # check domain setting (1 = checked box in settings)
            if send_to_google_sheet == 1:
                try:
                    service = build('sheets', 'v4', credentials=creds)
                    print(body)
                    result = service.spreadsheets().values().append(
                        spreadsheetId=spreadsheet_config['spreadsheet_id'],
                        range=spreadsheet_config['range'],
                        valueInputOption='RAW',
                        insertDataOption='INSERT_ROWS',
                        body=body
                    ).execute()
                    sent_to_sheets = '1'
                    print('Sent to Google Sheet Successfully')
                except HttpError as error: 
                    print('An error occurred while sending data to Google Sheets: ', error._get_reason())
                    sent_to_sheets = '0'
    
        # Insert the data into the database
        db_insertion_success = insert_data_into_db(data, sent_to_gronat, sent_to_sheets, validation)
        
        if db_insertion_success:
            session['submitted'] = True
            print('Successfully Submitted to Heroku database')
            return jsonify({"message": "Data sent to Heroku successfully."}), 200
        
        if not db_insertion_success and sent_to_gronat == '0':
            print("Database insertion failed. Sending data to the leads API...")
            response = requests.post(api_url, data=query_string)
            # If the insertion fails, send the data to the leads API
            if response.status_code >= 200 and response.status_code < 300:
                sent_to_gronat = '1'
                print('Successfully sent to Gronat as backup')
                return jsonify({"message": "Data sent to Heroku successfully."}), 200
            else:
                print('unable to send to gronat as backup')
                return jsonify({"message": "Failed to send data to Heroku."}), 400

        # Render the template with the updated data and message
        return render_template('home.html', current_user=current_user, data=data)
    
    # Render the home template on GET request
    return render_template('home.html', current_user=current_user)