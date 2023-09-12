#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from helpers import creds
from googleapiclient.discovery import build
from operator import attrgetter
from datetime import datetime, timedelta
import plotly.express as px
import plotly.offline as pyo

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

@table_bp.route('/charts')
@login_required
def show_charts():
    from models.lead import Lead

    filter_type = request.args.get('filter_type', default='all')
    specific_date = request.args.get('specific_date')
    week_start_date = request.args.get('week_start_date')
    month = request.args.get('month')

    def try_parsing_date(text):
        for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None

    def filter_leads_by_date(data, start_date, end_date):
        return [row for row in data if start_date <= try_parsing_date(row.timestamp) <= end_date]

    all_data = Lead.query.all()

    today = datetime.now()
    if filter_type == 'day' and specific_date:
        start_date = end_date = datetime.strptime(specific_date, '%Y-%m-%d')
    elif filter_type == 'weekly' and week_start_date:
        start_date = datetime.strptime(week_start_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=7)
    elif filter_type == 'monthly' and month:
        start_date = datetime(today.year, int(month), 1)
        next_month = int(month) % 12 + 1
        next_year = today.year if next_month != 1 else today.year + 1
        end_date = datetime(next_year, next_month, 1) - timedelta(days=1)
    else:
        start_date = datetime.min
        end_date = datetime.max

    all_data = filter_leads_by_date(all_data, start_date, end_date)

    label_counts = {}
    for row in all_data:
        label = row.label
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts[label] = 1

    labels = list(label_counts.keys())
    counts = list(label_counts.values())

    # Generate a custom title for the chart
    title_detail = ""
    if filter_type == 'day' and specific_date:
        title_detail = f", {specific_date}"
    elif filter_type == 'weekly' and week_start_date:
        end_week_date = (datetime.strptime(week_start_date, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d')
        title_detail = f", {week_start_date} to {end_week_date}"
    elif filter_type == 'monthly' and month:
        month_name = datetime(today.year, int(month), 1).strftime('%B')
        title_detail = f", {month_name}"

    title = f"Lead Counts by Label ({filter_type.capitalize()}{title_detail})"
    fig = px.bar(x=labels, y=counts, labels={'x': 'Label', 'y': 'Lead Count'}, title=title)
    chart_html = pyo.plot(fig, output_type='div')

    return render_template('charts.html', chart_html=chart_html, current_user=current_user, filter_type=filter_type)


@table_bp.route('/table')
@login_required
def show_table():
    from models.lead import Lead
    # Retrieve the current data from the Data table
    all_data = Lead.query.all()

    # Check if the "Show All Entries" button is clicked
    show_all = request.args.get('show_all')

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
    }

    if filter_by:
        # Filter the data based on the selected filter
        column_attribute = filter_columns.get(filter_by)
        if column_attribute:
            filter_value = request.args.get('filter_value', default="")
            filtered_data = [row for row in all_data if attrgetter(column_attribute)(row) == filter_value]
        else:
            # Invalid filter selected, show all data
            filtered_data = all_data

    # Check if "Show All Entries" button is clicked
    if show_all:
        filtered_data = all_data

    # Pagination
    per_page = 15
    page = request.args.get('page', 1, type=int)
    filtered_data = sorted(filtered_data, key=attrgetter('id'), reverse=True)

    if show_all:
        data = filtered_data
    else:
        # Calculate start and end index for pagination
        start = (page - 1) * per_page
        end = start + per_page
        data = filtered_data[start:end]

    # Determine the total number of pages
    total_pages = 1 if show_all else len(filtered_data) // per_page + (len(filtered_data) % per_page > 0)

    # Calculate start_page and end_page
    visible_pages = 5  # Number of visible page numbers excluding "..." separators
    start_page = max(page - visible_pages // 2, 1)
    end_page = min(start_page + visible_pages, total_pages)

    # Adjust start_page if end_page is at the maximum limit
    if end_page == total_pages:
        start_page = max(end_page - visible_pages + 1, 1)

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
        lead.sent_to_gronat = '1'
        db.session.commit()
        flash("Lead successfully sent to Gronat.", "success")
    else:
        flash("Failed to send lead to Gronat. Please try again.", "error")

    return redirect(url_for('table.show_table'))