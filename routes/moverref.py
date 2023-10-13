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


@moverref_bp.route('/edit_moverref_config/<int:config_id>', methods=['POST'])
def edit_moverref_config(config_id):
    from app import db
    from models.moverref_config import MoverrefConfig
    
    config = MoverrefConfig.query.get(config_id)

    if config:
        config.name = request.form['name']
        config.repeat_count = request.form['repeat_count']
        
        db.session.commit()

    return redirect(url_for('moverref.show_moverref_configs'))

@moverref_bp.route('/show_moverref_configs', methods=['GET'])
@login_required
def show_moverref_configs():
    from models.moverref_config import MoverrefConfig
    
    original_configs = MoverrefConfig.query.all()
    
    # Transform the original_configs
    transformed_configs = []
    for config in original_configs:
        # Assuming the email is stored in config.email, if it's a different attribute, replace accordingly.
        config.name = email_to_dept(config.name)
        transformed_configs.append(config)

    return render_template('moverref_configs.html', configs=transformed_configs, current_user=current_user)

@moverref_bp.route('/delete_moverref_config/<int:config_id>', methods=['POST'])
def delete_moverref_config(config_id):
    from app import db
    from models.moverref_config import MoverrefConfig

    config = MoverrefConfig.query.get(config_id)
    if config:
        db.session.delete(config)
        db.session.commit()

    return redirect(url_for('moverref.show_moverref_configs'))


