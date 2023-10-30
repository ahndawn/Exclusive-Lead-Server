from flask import Blueprint, render_template, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from helpers import email_to_dept

moverref_bp = Blueprint('moverref', __name__)

@moverref_bp.route('/add_moverref_config', methods=['POST'])
def add_moverref_config():
    from app import db
    from models.moverref_config import MoverrefConfig
    
    name = request.form['name']
    repeat_count = request.form['repeat_count']

    # Fetch the maximum sequence_order from the database
    max_sequence = db.session.query(db.func.max(MoverrefConfig.sequence_order)).scalar()
    if max_sequence is None:
        max_sequence = 0

    # Increment by 1 for the new configuration
    new_sequence = max_sequence + 1

    new_config = MoverrefConfig(name=name, sequence_order=new_sequence, repeat_count=repeat_count)
    
    db.session.add(new_config)
    db.session.commit()

    return redirect(url_for('moverref.show_moverref_configs'))

@moverref_bp.route('/add_moverref_config_db2', methods=['POST'])
def add_moverref_config_db2():
    from app import db
    from models.moverref_config import MoverrefConfig2
    
    name = request.form['name']
    repeat_count = request.form['repeat_count']

    # Fetch the maximum sequence_order from the database for DB2
    max_sequence = db.session.query(db.func.max(MoverrefConfig2.sequence_order)).scalar()
    if max_sequence is None:
        max_sequence = 0

    # Increment by 1 for the new configuration
    new_sequence = max_sequence + 1

    new_config = MoverrefConfig2(name=name, sequence_order=new_sequence, repeat_count=repeat_count)
    
    db.session.add(new_config)
    db.session.commit()

    return redirect(url_for('moverref.show_moverref_configs'))

@moverref_bp.route('/edit_moverref_config/<int:config_id>', methods=['POST'])
def edit_moverref_config(config_id):
    from app import db
    from models.moverref_config import MoverrefConfig
    
    config = MoverrefConfig.query.get(config_id)
    
    name_to_email = {
        'TA': 'customerservice@safeshipmoving.com',
        'TB': 'rachel.s@safeshipmoving.com',
        'TC': 'chris@safeshipmoving.com',
        'SL': 'leads@safeshipmoving.com',
        'LL': 'ahni@safeshipmoving.com',
        'EX': 'sales@safeshipmoving.com',
        'BL': 'max@safeshipmoving.com'
    }

    if config:
        config.name = request.form['name']
        config.name = name_to_email.get(config.name, config.name)
        config.repeat_count = request.form['repeat_count']

        db.session.commit()

    return redirect(url_for('moverref.show_moverref_configs'))

@moverref_bp.route('/edit_moverref_config_db2/<config_id>', methods=['POST'])
def edit_moverref_config_db2(config_id):
    from app import db
    from models.moverref_config import MoverrefConfig2

    name_to_email = {
        'TA': 'customerservice@safeshipmoving.com',
        'TB': 'rachel.s@safeshipmoving.com',
        'TC': 'chris@safeshipmoving.com',
        'SL': 'leads@safeshipmoving.com',
        'LL': 'ahni@safeshipmoving.com',
        'EX': 'sales@safeshipmoving.com'
    }

    config = MoverrefConfig2.query.get(config_id)

    if config:
        config.name = request.form['name']
        config.name = name_to_email.get(config.name, config.name)
        config.repeat_count = request.form['repeat_count']

        db.session.commit()

    return redirect(url_for('moverref.show_moverref_configs'))

@moverref_bp.route('/show_moverref_configs', methods=['GET'])
@login_required
def show_moverref_configs():
    from models.moverref_config import MoverrefConfig, MoverrefConfig2

    # Fetch and transform configs from both databases
    raw_configs_db1 = MoverrefConfig.query.all()
    raw_configs_db2 = MoverrefConfig2.query.all()

    configs_db1 = [transform_config_name(config) for config in raw_configs_db1]
    configs_db2 = [transform_config_name(config) for config in raw_configs_db2]

    return render_template('moverref_configs.html',
                           configs_db1=configs_db1,
                           raw_configs_db1=raw_configs_db1,
                           configs_db2=configs_db2,
                           raw_configs_db2=raw_configs_db2,
                           current_user=current_user)

def transform_config_name(config):
    config.name = email_to_dept(config.name)
    return config

@moverref_bp.route('/delete_moverref_config/<int:config_id>', methods=['POST'])
def delete_moverref_config(config_id):
    from app import db
    from models.moverref_config import MoverrefConfig

    config = MoverrefConfig.query.get(config_id)
    if config:
        db.session.delete(config)
        db.session.commit()

    return redirect(url_for('moverref.show_moverref_configs'))

@moverref_bp.route('/delete_moverref_config_db2/<int:config_id>', methods=['POST'])
def delete_moverref_config_db2(config_id):
    from app import db
    from models.moverref_config import MoverrefConfig2

    config = MoverrefConfig2.query.get(config_id)
    if config:
        db.session.delete(config)
        db.session.commit()

    return redirect(url_for('moverref.show_moverref_configs'))


