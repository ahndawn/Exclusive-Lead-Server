#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, request, jsonify, render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from helpers import email_to_dept
from googleapiclient.discovery import build
from operator import attrgetter
from sqlalchemy import cast, Date
from datetime import datetime

react_home_bp = Blueprint('react', __name__)

@react_home_bp.route('/lead_count_by_label', methods=['GET'])
@login_required
def get_lead_count_by_label():
    from app import db
    from models.lead import Lead
    lead_counts = db.session.query(Lead.label, db.func.count(Lead.label)).group_by(Lead.label).all()
    result = {label: count for label, count in lead_counts}
    return jsonify(result)