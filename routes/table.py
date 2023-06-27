#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template 
from flask_login import login_required, current_user
from helpers import creds
from googleapiclient.discovery import build

table_bp = Blueprint('table', __name__)


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
            filtered_data = Lead.query.filter(column_attribute == filter_value).all()
        else:
            # Invalid filter selected, show all data
            filtered_data = all_data

    # Check if "Show All Entries" button is clicked
    if show_all:
        filtered_data = all_data

    # Pagination
    per_page = 15
    page = request.args.get('page', 1, type=int)

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