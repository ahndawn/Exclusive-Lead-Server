#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required

domain_bp = Blueprint('domain', __name__)

@domain_bp.route('/domains', methods=['GET'])
@login_required
def show_domains():
    from models.domain import Domain
    from forms.forms import DomainForm
    form = DomainForm()
    domains = Domain.query.all()
    return render_template('domains.html', domains=domains, form=form)

@domain_bp.route('/get_domain_info/<label>', methods=['GET'])
def get_domain_info(label):
    from models.domain import Domain
    domain = Domain.query.filter_by(label=label).first()
    if domain:
        change_moverref = domain.change_moverref
        print(f'Posting key (moverref) set to: {change_moverref}')
        return jsonify({
            'label': domain.label,
            'domain': domain.domain,
            'd_phone_number': domain.d_phone_number,
            'lead_cost' : domain.lead_cost,
            'send_to_leads_api': domain.send_to_leads_api,
            'send_to_google_sheet': domain.send_to_google_sheet,
            'twilio_number_validation': domain.twilio_number_validation,
            'sms_texting': domain.sms_texting,
            'change_moverref': domain.change_moverref,
            'moverref': domain.moverref
        })
    else:
        return jsonify({'error': 'Domain not found'}), 404

@domain_bp.route('/update_domain/<label>', methods=['POST'])
def update_domain(label):
    from app import db
    from models.domain import Domain
    original_label = request.form['original_label']
    label = request.form['label']
    domain = request.form['domain']
    lead_cost = request.form['lead_cost']
    d_phone_number = request.form['phone_number']
    moverref = request.form['moverref']
    send_to_leads_api = request.form.get('send_to_leads_api', '0') == '1'
    send_to_google_sheet = request.form.get('send_to_google_sheet', '0') == '1'
    twilio_number_validation = request.form.get('twilio_number_validation', '0') == '1'
    sms_texting = request.form.get('sms_texting', '0') == '1'
    change_moverref = request.form.get('change_moverref', '0') == '1'
    print(f'Posting key (moverref) set to: {change_moverref}')

    # Convert the values to integer 1 if they are True, 0 if they are False
    send_to_leads_api = int(send_to_leads_api)
    send_to_google_sheet = int(send_to_google_sheet)
    twilio_number_validation = int(twilio_number_validation)
    sms_texting = int(sms_texting)
    change_moverref = int(change_moverref)

    domain_object = Domain.query.filter_by(label=original_label).first()
    if domain_object:
        domain_object.label = label
        domain_object.domain = domain
        domain_object.lead_cost = lead_cost
        domain_object.d_phone_number = d_phone_number
        domain_object.send_to_leads_api = send_to_leads_api
        domain_object.send_to_google_sheet = send_to_google_sheet
        domain_object.twilio_number_validation = twilio_number_validation
        domain_object.sms_texting = sms_texting
        domain_object.moverref = moverref
        domain_object.change_moverref = change_moverref
        db.session.commit()

    return redirect(url_for('domain.show_domains'))

@domain_bp.route('/insert_domain', methods=['POST'])
def insert_domain():
    from app import db
    from forms.forms import DomainForm
    from models.domain import Domain
    form = DomainForm()
    if form.validate_on_submit():
        label = form.label.data
        domain_name = form.domain.data
        d_phone_number = form.d_phone_number.data
        send_to_leads_api = 1
        send_to_google_sheet = 1
        twilio_number_validation = 1
        sms_texting = 1
        lead_cost = '110'


        new_domain = Domain(
            label=label,
            domain=domain_name,
            d_phone_number=d_phone_number,
            lead_cost=lead_cost,
            send_to_leads_api=send_to_leads_api,
            send_to_google_sheet=send_to_google_sheet,
            twilio_number_validation=twilio_number_validation,
            sms_texting=sms_texting,
            change_moverref = True,
            moverref = 'chris@safeshipmoving.com'
        )

        try:
            db.session.add(new_domain)
            db.session.commit()
            flash('Domain added successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')

    else:
        # If the form is not valid, flash error messages
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {getattr(form, field).label.text}: {error}', 'error')

    return redirect(url_for('domain.show_domains'))

@domain_bp.route('/delete_domain/<label>', methods=['POST'])
def delete_domain(label):
    from app import db
    from models.domain import Domain
    if label:
        if label == 'all':
            Domain.query.delete()
        else:
            domain = Domain.query.filter_by(label=label).first()
            if domain:
                db.session.delete(domain)
        db.session.commit()

    return redirect(url_for('domain.show_domains'))