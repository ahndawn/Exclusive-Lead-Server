#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from helpers import creds
from googleapiclient.discovery import build
from operator import attrgetter
from sqlalchemy import func

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
@table_bp.route('/get_moverref_data')
def get_moverref_data():
    from app import db
    from models.lead import Lead
    # Aggregate data by moverref and count leads for each moverref
    results = db.session.query(Lead.moverref, func.count(Lead.id)).group_by(Lead.moverref).filter(Lead.moverref.isnot(None)).all()

    # Convert results into a dictionary format for JSON
    data = {result[0]: result[1] for result in results}

    return jsonify(data)

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


@table_bp.route('/table')
@login_required
def show_table():
    from models.lead import Lead
    # Retrieve the current data from the Data table
    all_data = Lead.query.all()

    # Get the filter from the query parameters
    filter_by = request.args.get('filter', default=None)
    filtered_data = all_data

    filter_columns = {
        'timestamp': Lead.timestamp,
        'label': Lead.label,
        'firstname': Lead.firstname,
        'email': Lead.email,
        'phone1': Lead.phone1,
        'ozip': Lead.ozip,
        'dzip': Lead.dzip,
        'dcity': Lead.dcity,
        'dstate': Lead.dstate,
        'movesize': Lead.movesize,
        'movedte': Lead.movedte,
        'conversion': Lead.conversion,
        'validation': Lead.validation,
        'notes': Lead.notes,
        'sent_to_gronat': Lead.sent_to_gronat,
        'sent_to_sheets': Lead.sent_to_sheets,
        'moverref': Lead.moverref,
    }

    column_attribute = filter_columns.get(filter_by)
    if column_attribute:
        filter_value = request.args.get('filter_value', default="")
        if filter_by in ['sent_to_gronat', 'sent_to_sheets']:
            try:
                filter_value = int(filter_value)
                # For these specific columns, cast the integer filter_value to string for the query
                filtered_data = Lead.query.filter(getattr(Lead, filter_by).like(f"%{filter_value}%")).all()
            except ValueError:
                return flash("Invalid integer value provided for filter")
        else:
            filtered_data = Lead.query.filter(getattr(Lead, filter_by).like(f"%{filter_value}%")).all()
    else:
    # Invalid filter selected, show all data
        filtered_data = all_data
    
    # Check if the "Show All Entries" button is clicked or a filter is applied
    show_all = request.args.get('show_all') or filter_by
    
    filtered_data = sorted(filtered_data, key=attrgetter('id'), reverse=True)
    
    page = request.args.get('page', 1, type=int)

    if show_all:
        data = filtered_data
    else:
    # Pagination
        per_page = 25
        start = (page - 1) * per_page
        end = start + per_page
        data = filtered_data[start:end]

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
        'data': data,
        'enumerate': enumerate,
        'page': page,
        'total_pages': total_pages,
        'show_pagination': total_pages > 1,
        'start_page': start_page,
        'end_page': end_page
    }

    # Render the template with the current data and pagination information
    return render_template('table.html', **template_context, current_user=current_user)

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
        if filter_by in ['sent_to_gronat', 'sent_to_sheets']:
            try:
                filter_value = int(filter_value)
                # For these specific columns, cast the integer filter_value to string for the query
                filtered_data = LocalLead.query.filter(getattr(LocalLead, filter_by).like(f"%{filter_value}%")).all()
            except ValueError:
                return flash("Invalid integer value provided for filter")
        else:
            filtered_data = LocalLead.query.filter(getattr(LocalLead, filter_by).like(f"%{filter_value}%")).all()
    else:
    # Invalid filter selected, show all data
        filtered_data = all_data
    
    # Check if the "Show All Entries" button is clicked or a filter is applied
    show_all = request.args.get('show_all') or filter_by
    
    filtered_data = sorted(filtered_data, key=attrgetter('id'), reverse=True)
    
    page = request.args.get('page', 1, type=int)

    if show_all:
        data = filtered_data
    else:
    # Pagination
        per_page = 25
        start = (page - 1) * per_page
        end = start + per_page
        data = filtered_data[start:end]

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
        'data': data,
        'enumerate': enumerate,
        'page': page,
        'total_pages': total_pages,
        'show_pagination': total_pages > 1,
        'start_page': start_page,
        'end_page': end_page
    }

    # Render the template with the current data and pagination information
    return render_template('local_lead_table.html', **template_context, current_user=current_user)

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

@table_bp.route('/send_local_gronat', methods=['POST'])
def send_to_local_route():
    from helpers import send_to_gronat
    from app import db
    from models.domain import Domain
    lead_id = request.form['lead_id']
    
    # Fetch lead details from the database using lead_id
    lead = get_local_details_from_db(lead_id)
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




