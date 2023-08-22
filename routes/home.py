#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template, session
from flask_login import current_user
from urllib.parse import unquote
from helpers import client, send_message, format_phone_number, format_move_date, send_email, send_to_gronat, send_to_sheets
from datetime import datetime
import pytz


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
        print(f"--------> INCOMING: {data}")

        # if form post request has start/end state/city or not
        ozip = data.get('ozip', '')
        dcity = data.get('dcity', '')
        dstate = data.get('dstate', '')
        dzip = data.get('dzip', '')
        email = data.get('email')
        label = data.get('label')
        
        #create timestamp
        timezone = pytz.timezone('America/New_York')
        current_datetime = datetime.now(timezone)
        timestamp = current_datetime.strftime('%Y-%m-%d')

        phnumber = data.get('phone1')
        phone_number = format_phone_number(phnumber)

        domain = Domain.query.filter_by(label=label).first()
        change_moverref = domain.change_moverref
    
        movedate = data.get('movedte')
        movedte = format_move_date(movedate)

        movesize = data.get('movesize')

        if '1' not in movesize and '2' not in movesize and 'Studio' not in movesize and change_moverref == True:
            moverref = 'forwarding@safeshipmoving.com'
        else:
            moverref = data.get('moverref')
        print(f'Posting Key (moverref) is: {moverref}')

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

        
        #############send to gronat function from helpers.py
        sent_gronat_success = send_to_gronat(label, moverref, first_name, email, phone_number, ozip, dzip, dcity, dstate, data, movedte, send_to_leads_api)
        if sent_gronat_success:
            sent_to_gronat = '1'
        else:
            sent_to_gronat = '0'

        ################send to email function from helpers.py
        send_email(label,dzip,dcity,dstate,ref_no, email, data, movedte, ozip, phone_number, first_name)
        
        ################## TWILIO
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
        
        ############################## Send to sheets
        # default value '0' if not sent to sheet, '1' if sent. use spreadsheet_config dictionary
        if send_to_google_sheet == 1:
            lead_cost = domain_settings.lead_cost if domain_settings else "110"
            sent_to_sheets_success=send_to_sheets(timestamp,first_name,ozip,dzip,dcity,dstate,data,ref_no,validation,label, phone_number, lead_cost)
            if sent_to_sheets_success:
                sent_to_sheets='1'
            else:
                sent_to_sheets='0'
        
        ############################### Insert the data into the database
        db_insertion_success = insert_data_into_db(data, sent_to_gronat, sent_to_sheets, validation, movesize, movedte)
    
        if db_insertion_success:
            session['submitted'] = True
            print("END <--------")
            return jsonify({"message": "Data sent to Heroku successfully."}), 200
            
        
        if not db_insertion_success and sent_to_gronat == '0':
            print("Database insertion failed. Sending data to the leads API...")
            send_to_gronat(label, moverref, first_name, email, phone_number, ozip, dzip, dcity, dstate, data, movedte, send_to_leads_api, sent_to_gronat)
            # If the insertion fails, send the data to the leads API as long as it wasn't sent already

        # Render the template with the updated data and message
        return render_template('home.html', current_user=current_user, data=data)
    
    # Render the home template on GET request
    return render_template('home.html', current_user=current_user)