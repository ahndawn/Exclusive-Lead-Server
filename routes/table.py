#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from helpers import email_to_dept
from googleapiclient.discovery import build
from operator import attrgetter
from sqlalchemy import cast, Date,Integer, cast
from datetime import datetime

table_bp = Blueprint('table', __name__)

def get_lead_details_from_db(lead_id):
    from models.lead import Lead
    """
    Fetches a lead from the database by its ID.
    
    :param lead_id: ID of the lead to fetch.
    :return: Lead object if found, None otherwise.
    """
    lead = Lead.query.get(lead_id)
    return lead

def get_local_details_from_db(lead_id):
    from models.locallead import LocalLead
    """
    Fetches a lead from the database by its ID.
    
    :param lead_id: ID of the lead to fetch.
    :return: Lead object if found, None otherwise.
    """
    lead = LocalLead.query.get(lead_id)
    return lead


##################### shows all leads and their moverrefs chart
@table_bp.route('/get_moverref_data')
def get_moverref_data():
    from app import db
    from models.lead import Lead, Lead2
    from models.locallead import LocalLead
    from sqlalchemy import func

    # Extract start_date and end_date from request arguments
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # If start_date and end_date are provided, format them for the query filter
    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        leads_query1 = Lead.query.filter(cast(Lead.timestamp, Date).between(start_date_obj, end_date_obj))
        leads_query2 = Lead2.query.filter(cast(Lead2.timestamp, Date).between(start_date_obj, end_date_obj))
        local_leads_query = LocalLead.query.filter(cast(LocalLead.timestamp, Date).between(start_date_obj, end_date_obj))
    else:
        leads_query1 = Lead.query
        leads_query2 = Lead2.query
        local_leads_query = LocalLead.query

    # Aggregate data by moverref and count leads for each moverref from db1
    results1 = (leads_query1.with_entities(Lead.moverref, func.count(Lead.id))
               .group_by(Lead.moverref)
               .filter(Lead.moverref.isnot(None))
               .all())

    # Aggregate data by moverref and count leads for each moverref from db2
    results2 = (leads_query2.with_entities(Lead2.moverref, func.count(Lead2.id))
               .group_by(Lead2.moverref)
               .filter(Lead2.moverref.isnot(None))
               .all())

    # Aggregate data by moverref and count local leads for each moverref
    results3 = (local_leads_query.with_entities(LocalLead.moverref, func.count(LocalLead.id))
               .group_by(LocalLead.moverref)
               .filter(LocalLead.moverref.isnot(None))
               .all())

    # Convert results into a dictionary format for JSON, combining results from all databases
    data = {}
    for result in results1 + results2 + results3:
        key = email_to_dept(result[0])
        data[key] = data.get(key, 0) + result[1]

    return jsonify(data)

##########################show all leads by label(lead provider) chart
@table_bp.route('/get_label_data')
def get_label_data():
    from app import db
    from models.lead import Lead, Lead2
    from models.locallead import LocalLead  # Import the LocalLead model
    from sqlalchemy import func

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Initial setup for queries
    query_base = Lead.query
    query_base2 = Lead2.query
    query_base3 = LocalLead.query  # Query base for LocalLead

    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        query_base = query_base.filter(cast(Lead.timestamp, Date).between(start_date_obj, end_date_obj))
        query_base2 = query_base2.filter(cast(Lead2.timestamp, Date).between(start_date_obj, end_date_obj))
        query_base3 = query_base3.filter(cast(LocalLead.timestamp, Date).between(start_date_obj, end_date_obj))  # Filter for LocalLead

    # Query for Lead model
    results1 = (query_base.with_entities(Lead.label, func.count(Lead.id))
               .group_by(Lead.label)
               .filter(Lead.label.isnot(None))
               .all())

    # Query for Lead2 model
    results2 = (query_base2.with_entities(Lead2.label, func.count(Lead2.id))
               .group_by(Lead2.label)
               .filter(Lead2.label.isnot(None))
               .all())

    # Query for LocalLead model
    results3 = (query_base3.with_entities(LocalLead.label, func.count(LocalLead.id))
               .group_by(LocalLead.label)
               .filter(LocalLead.label.isnot(None))
               .all())  # Aggregation for LocalLead

    # Merge results
    combined_results = {}
    for label, count in results1 + results2 + results3:  # Include results3 in the merging process
        combined_results[label] = combined_results.get(label, 0) + count

    return jsonify(combined_results)
    
###############for updating moverref on leads table
@table_bp.route('/update_moverref', methods=['POST'])
def update_moverref():
    from app import db
    from models.lead import Lead
    lead_id = request.form['lead_id']
    new_moverref = request.form['new_value']

    lead = Lead.query.get(lead_id)
    if not lead:
        return jsonify({"success": False, "message": "Lead not found."}), 404

    lead.moverref = new_moverref
    db.session.commit()

    return jsonify({"success": True})

####################for updating moverref on local leads table
@table_bp.route('/update_local_moverref', methods=['POST'])
def update_local_moverref():
    from app import db
    from models.locallead import LocalLead
    lead_id = request.form['lead_id']
    new_moverref = request.form['new_value']

    lead = LocalLead.query.get(lead_id)
    if not lead:
        return jsonify({"success": False, "message": "Lead not found."}), 404

    lead.moverref = new_moverref
    db.session.commit()

    return jsonify({"success": True})

######################## Exclusive leads table
@table_bp.route('/table')
@login_required
def show_table():
    from models.locallead import LocalLead
    from models.lead import Lead 
    from models.lead import Lead2
    # Retrieve the current data from the Lead table
    all_data = Lead.query.all()

    # Get the filter from the query parameters
    filter_by = request.args.get('filter', default=None)
    filter_value = request.args.get('filter_value', default="")

    # Add new parameters to handle the unsent leads button and show all entries
    show_unsent = request.args.get('show_unsent', 'false').lower() == 'true'
    show_all = request.args.get('show_all', 'false').lower() == 'true'

    if show_unsent:
        # Filter for unsent leads
        query1 = Lead2.query.filter(cast(Lead2.sent_to_gronat, Integer) == 0).all()
        query2 = LocalLead.query.filter(cast(LocalLead.sent_to_gronat, Integer) == 0).all()
        query3 = Lead.query.filter(cast(Lead.sent_to_gronat, Integer) == 0).all()
        filtered_data = query1 + query2 + query3
        show_all = True
        # Check if filtered_data is empty
        if not filtered_data:
            flash('All leads have been successfully sent to Gronat', 'success') 
    elif filter_by:
        # Apply filter based on column
        try:
            if filter_by in ['sent_to_gronat', 'sent_to_sheets']:
                filter_value = int(filter_value)
            column = getattr(Lead, filter_by)
            filtered_data = Lead.query.filter(column.like(f"%{filter_value}%")).all()
        except (ValueError, AttributeError):
            flash("Invalid filter")
            filtered_data = all_data
    else:
        # Default case, no filtering
        filtered_data = all_data

    # Sorting and Pagination Logic
    filtered_data = sorted(filtered_data, key=attrgetter('id'), reverse=True)
    
    page = request.args.get('page', 1, type=int)
    per_page = 25
    if show_all:
        data = filtered_data
    else:
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        data = filtered_data[start:end]

    leads = [
        {
            'id': lead.id,
            'timestamp': lead.timestamp,
            'label': lead.label,
            'firstname': lead.firstname,
            'email': lead.email,
            'phone1': lead.phone1,
            'ozip': lead.ozip,
            'dzip': lead.dzip,
            'dcity': lead.dcity,
            'dstate': lead.dstate,
            'movesize': lead.movesize,
            'movedte': lead.movedte,
            'conversion': lead.conversion,
            'validation': lead.validation,
            'notes': lead.notes,
            'sent_to_gronat': lead.sent_to_gronat,
            'sent_to_sheets': lead.sent_to_sheets,
            'moverref': email_to_dept(lead.moverref), 
        }
        for lead in data
    ]

    # Determine the total number of pages
    total_pages = len(filtered_data) // per_page + (len(filtered_data) % per_page > 0)

    # Calculate start_page and end_page
    visible_pages = 5
    start_page = max(page - visible_pages // 2, 1)
    end_page = min(start_page + visible_pages, total_pages)

    # Adjust start_page if end_page is at the maximum limit
    if end_page == total_pages:
        start_page = max(end_page - visible_pages + 1, 1)

    # If showing all, set these values to avoid errors in the frontend
    if show_all:
        total_pages, start_page, end_page = 1, 1, 1

    # Add the enumerate function to the template context
    template_context = {
        'data': leads,
        'enumerate': enumerate,
        'page': page,
        'total_pages': total_pages,
        'show_pagination': total_pages > 1,
        'start_page': start_page,
        'end_page': end_page
    }

    # Render the template with the current data and pagination information
    return render_template('table.html', **template_context, current_user=current_user)

#########################Local leads table
@table_bp.route('/local-table')
@login_required
def show_local():
    from models.locallead import LocalLead
    # Retrieve the current data from the Data table
    all_data = LocalLead.query.all()

    # Get the filter from the query parameters
    filter_by = request.args.get('filter', default=None)
    filtered_data = all_data

    filter_columns = {
        'timestamp': LocalLead.timestamp,
        'label': LocalLead.label,
        'firstname': LocalLead.firstname,
        'email': LocalLead.email,
        'phone1': LocalLead.phone1,
        'ozip': LocalLead.ozip,
        'dzip': LocalLead.dzip,
        'dcity': LocalLead.dcity,
        'dstate': LocalLead.dstate,
        'movesize': LocalLead.movesize,
        'movedte': LocalLead.movedte,
        'conversion': LocalLead.conversion,
        'validation': LocalLead.validation,
        'notes': LocalLead.notes,
        'sent_to_gronat': LocalLead.sent_to_gronat,
        'sent_to_sheets': LocalLead.sent_to_sheets,
        'moverref': LocalLead.moverref,
    }

    column_attribute = filter_columns.get(filter_by)
    if column_attribute:
        filter_value = request.args.get('filter_value', default="")
    
        if filter_by == 'moverref':
            # Handle the special case for 'moverref'
            filtered_data = [
                lead for lead in all_data 
                if lead.moverref and 
                (lambda x: x and x.lower().startswith(filter_value.lower()))(email_to_dept(lead.moverref))
            ]
        elif filter_by in ['sent_to_gronat', 'sent_to_sheets']:
            try:
                filter_value = int(filter_value)
                filtered_data = LocalLead.query.filter(getattr(LocalLead, filter_by).like(f"%{filter_value}%")).all()
            except ValueError:
                return flash("Invalid integer value provided for filter")
        else:
            filtered_data = LocalLead.query.filter(getattr(LocalLead, filter_by).like(f"%{filter_value}%")).all()
    else:
        filtered_data = all_data
    
    # Check if the "Show All Entries" button is clicked or a filter is applied
    show_all = request.args.get('show_all') or filter_by
    
    filtered_data = sorted(filtered_data, key=attrgetter('id'), reverse=True)
    
    page = request.args.get('page', 1, type=int)

    per_page = 25
    if show_all:
        data = filtered_data
    else:
    # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        data = filtered_data[start:end]

    leads = [
    {
        'id': lead.id,
        'timestamp': lead.timestamp,
        'label': lead.label,
        'firstname': lead.firstname,
        'email': lead.email,
        'phone1': lead.phone1,
        'ozip': lead.ozip,
        'dzip': lead.dzip,
        'dcity': lead.dcity,
        'dstate': lead.dstate,
        'movesize': lead.movesize,
        'movedte': lead.movedte,
        'conversion': lead.conversion,
        'validation': lead.validation,
        'notes': lead.notes,
        'sent_to_gronat': lead.sent_to_gronat,
        'sent_to_sheets': lead.sent_to_sheets,
        'moverref': email_to_dept(lead.moverref),  # Convert moverref here
    }
    for lead in data
]

    # Determine the total number of pages
    total_pages = len(filtered_data) // per_page + (len(filtered_data) % per_page > 0)

    # Calculate start_page and end_page
    visible_pages = 5  # Number of visible page numbers excluding "..." separators
    start_page = max(page - visible_pages // 2, 1)
    end_page = min(start_page + visible_pages, total_pages)

    # Adjust start_page if end_page is at the maximum limit
    if end_page == total_pages:
        start_page = max(end_page - visible_pages + 1, 1)

    # If showing all, set these values to avoid errors in the frontend
    if show_all:
        total_pages, start_page, end_page = 1, 1, 1

    # Add the enumerate function to the template context
    template_context = {
        'data': leads,
        'enumerate': enumerate,
        'page': page,
        'total_pages': total_pages,
        'show_pagination': total_pages > 1,
        'start_page': start_page,
        'end_page': end_page
    }

    # Render the template with the current data and pagination information
    return render_template('local_lead_table.html', **template_context, current_user=current_user)

#############
@table_bp.route('/delete_lead/<int:lead_id>', methods=['POST'])
def delete_lead(lead_id):
    from app import db
    from models.lead import Lead, Lead2
    from models.locallead import LocalLead

    # Attempt to find the lead in each table
    lead = Lead.query.get(lead_id)
    if not lead:
        lead = LocalLead.query.get(lead_id)
    if not lead:
        lead = Lead2.query.get(lead_id)

    # If a lead is found, delete it
    if lead:
        db.session.delete(lead)
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(fail=False), 404

############send all leads on table to gronat
@table_bp.route('/send_all_local_gronat', methods=['POST'])
def send_all_to_local_gronat():
    from app import db 
    from helpers import send_to_gronat
    lead_ids = request.json.get('lead_ids', [])
    success_count = 0

    for lead_id in lead_ids:
        lead = get_local_details_from_db(lead_id)
        if lead and lead.sent_to_gronat == 0:
            # Call your send_to_gronat function here
            success = send_to_gronat(...)  # Fill in the arguments as needed
            if success:
                lead.sent_to_gronat = 1
                db.session.commit()
                success_count += 1

    if success_count == len(lead_ids):
        return jsonify(success=True, message="All leads successfully sent to GRONAT.")
    else:
        return jsonify(success=False, message="Some leads could not be sent. Please try again.")



######################for sending data to gronat from table if it was unsuccessful the first time.
@table_bp.route('/send_to_gronat', methods=['POST'])
def send_to_gronat_route():
    from helpers import send_to_gronat
    from app import db
    from models.domain import Domain
    lead_id = request.form['lead_id']
    
    # Fetch lead details from the database using lead_id
    lead = get_lead_details_from_db(lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for('table.show_table'))
    
    domain = Domain.query.filter_by(label=lead.label).first()
    if not domain:
        flash("Domain for the lead not found.", "error")
        return redirect(url_for('table.show_table'))
    
    moverref = domain.moverref
    icid = lead.notes  # Assuming ICID is stored as a note, adjust if needed

    # Extract other necessary details from the `lead` and `domain` objects
    label = lead.label
    first_name = lead.firstname
    email = lead.email
    phone_number = lead.phone1
    ozip = lead.ozip
    dzip = lead.dzip
    dcity = lead.dcity
    dstate = lead.dstate
    data = {"movesize": lead.movesize}  # Add other necessary fields if needed
    movedte = lead.movedte
    send_to_leads_api = domain.send_to_leads_api
    
    success = send_to_gronat(label, moverref, first_name, email, phone_number, ozip, dzip, dcity, dstate, data, movedte, send_to_leads_api, icid)

    if success:
    # Update the lead record in the database to reflect that it was successfully sent
        lead.sent_to_gronat = 1
        db.session.commit()
        return jsonify(success=True, message="Lead successfully sent to GRONAT.")
    else:
        return jsonify(success=False, message="Failed to send lead to Gronat. Please try again.")


######################for sending data to gronat from local leads table if it was unsuccessful the first time.
@table_bp.route('/send_local_gronat', methods=['POST'])
def send_to_local_route():
    from helpers import send_to_gronat
    from app import db
    lead_id = request.form['lead_id']
    
    
    # Fetch lead details from the database using lead_id
    lead = get_local_details_from_db(lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for('table.show_table'))
    
    moverref = 'ahni@safeshipmoving.com'
    icid = lead.notes  # Assuming ICID is stored as a note, adjust if needed

    # Extract other necessary details from the `lead` and `domain` objects
    label = lead.label
    first_name = lead.firstname
    email = lead.email
    phone_number = lead.phone1
    ozip = lead.ozip
    dzip = lead.dzip
    dcity = lead.dcity
    dstate = lead.dstate
    data = {"movesize": lead.movesize}  # Add other necessary fields if needed
    movedte = lead.movedte
    send_to_leads_api = 1
    
    success = send_to_gronat(label, moverref, first_name, email, phone_number, ozip, dzip, dcity, dstate, data, movedte, send_to_leads_api, icid)

    if success:
    # Update the lead record in the database to reflect that it was successfully sent
        lead.sent_to_gronat = 1
        db.session.commit()
        return jsonify(success=True, message="Lead successfully sent to GRONAT.")
    else:
        return jsonify(success=False, message="Failed to send lead to Gronat. Please try again.")


###################for updating move date on exclusive leads table
@table_bp.route('/update_movedte', methods=['POST'])
def update_movedte():
    from app import db
    lead_id = request.form['lead_id']
    new_movedte = request.form['new_value']

    lead = get_lead_details_from_db(lead_id)
    if not lead:
        return jsonify({"success": False, "message": "Lead not found."}), 404

    lead.movedte = new_movedte
    db.session.commit()

    return jsonify({"success": True})




##########################for updating local leads move date
@table_bp.route('/update_local_movedte', methods=['POST'])
def update_local_movedte():
    from app import db
    lead_id = request.form['lead_id']
    new_movedte = request.form['new_value']

    lead = get_local_details_from_db(lead_id)
    if not lead:
        return jsonify({"success": False, "message": "Lead not found."}), 404

    lead.movedte = new_movedte
    db.session.commit()

    return jsonify({"success": True})




