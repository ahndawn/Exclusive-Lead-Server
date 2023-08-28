#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template 
from flask_login import login_required, current_user
from helpers import creds
from googleapiclient.discovery import build
from operator import attrgetter
import plotly.express as px
import plotly.offline as pyo

table_bp = Blueprint('table', __name__)

# @table_bp.route('/charts')
# @login_required
# def show_charts():
#     from models.lead import Lead
#     import pandas as pd  # Import pandas for DataFrame creation
#     import plotly.express as px  # Import Plotly Express

#     today_start = datetime.now(pytz.timezone('America/New_York')).replace(hour=0, minute=0, second=0, microsecond=0)
#     week_start = today_start - timedelta(days=today_start.weekday())
#     month_start = today_start.replace(day=1)

#     all_data = Lead.query.all()

#     # Convert the saved timestamp strings to datetime objects
#     timezone = pytz.timezone('America/New_York')
#     for lead in all_data:
    #     lead.timestamp = datetime.strptime(lead.timestamp, '%Y-%m-%d').replace(tzinfo=timezone)

    # # Filter lead data for different time intervals
    # leads_today = [lead for lead in all_data if lead.timestamp >= today_start]
    # leads_week = [lead for lead in all_data if lead.timestamp >= week_start]
    # leads_month = [lead for lead in all_data if lead.timestamp >= month_start]

    # # Calculate lead counts for different time intervals
    # lead_count_today = len(leads_today)
    # lead_count_week = len(leads_week)
    # lead_count_month = len(leads_month)

    # # Create a DataFrame for Plotly
    # data = pd.DataFrame({
    #     'Time Interval': ['Today', 'This Week', 'This Month'],
    #     'Lead Count': [lead_count_today, lead_count_week, lead_count_month]
    # })

    # # Create a bar chart with Plotly
    # fig = px.bar(data, x='Time Interval', y='Lead Count', title='Lead Counts for Different Time Intervals')

    # # You can customize the chart appearance if needed
    # fig.update_layout(xaxis_title='Time Interval', yaxis_title='Lead Count')

    # # Convert the Plotly figure to HTML
    # chart_html = fig.to_html()

    # # Render the template with the chart
    # return render_template('charts.html', chart_html=chart_html, current_user=current_user, leads_today=leads_today, leads_week=leads_week, leads_month=leads_month)
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
    # Retrieve the current data from the Data table
    all_data = Lead.query.all()
    
    # Group data by label and count the leads
    label_counts = {}
    for row in all_data:
        label = row.label
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts[label] = 1
    
    labels = list(label_counts.keys())
    counts = list(label_counts.values())
    
    # Create a bar chart using Plotly
    fig = px.bar(x=labels, y=counts, labels={'x': 'Label', 'y': 'Lead Count'}, title='Lead Counts by Label')
    
    # Convert the Plotly figure to HTML
    chart_html = pyo.plot(fig, output_type='div')
    
    # Render the template with the chart
    return render_template('charts.html', chart_html=chart_html, current_user=current_user)


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
    lead_id = request.form['lead_id']
    moverref = 'chris@safeshipmoving.com'
    
    # Fetch lead details from the database using lead_id
    lead = get_lead_details_from_db(lead_id)  # Dummy function, replace with your actual function
    
    # Assuming `lead` is an object or dictionary containing all the required fields
    success = send_to_gronat(
        lead.label, 
        moverref, 
        lead.firstname, 
        lead.email, 
        lead.phone1, 
        lead.ozip, 
        lead.dzip, 
        lead.dcity, 
        lead.dstate, 
        {'movesize': lead.movesize, 'notes': lead.notes}, 
        lead.movedte,
        1
    )

    if success:
        lead.sent_to_gronat = '1'
        # db_update_sent_to_gronat(lead_id) // Dummy function, replace with your actual function
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})