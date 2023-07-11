#some imports are used within each required route and function in order to avoid 'circular imports'
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_user, logout_user, login_required, LoginManager
from forms.users import RegistrationForm, ForgotPasswordForm, ResetPasswordForm, LoginForm
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import bcrypt
from datetime import datetime, timedelta
import secrets
import os

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()

def generate_reset_token():
    return secrets.token_hex(16)

def is_reset_token_expired(token_expiration):
    expiration = datetime.strptime(token_expiration, '%Y-%m-%d %H:%M:%S.%f')
    return datetime.now() > expiration

email_key = os.environ.get('EMAIL_KEY')
certs = os.environ.get('REQUESTS_CA_BUNDLE')

def send_password_reset_email(user):
    token = user.reset_token
    email = user.email
    subject = 'Password Reset Request'
    template = 'reset_email.html'

    message = Mail(
        from_email='<ahni@safeshipmoving.com>',
        to_emails=[email],
        subject=subject,
        html_content=render_template(template, user=user, token=token)
    )

    try:
        sg = SendGridAPIClient(api_key=current_app.config['SENDGRID_API_KEY'])
        response = sg.send(message)
        print('Password reset email sent successfully.')
    except Exception as e:
        print('An error occurred while sending the password reset email:', str(e))


@login_manager.user_loader
def load_user(username):
    from models.user import User
    return User.query.get(username)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from models.user import User
    form = LoginForm()
    if form.validate_on_submit():
        # Query the user by username
        user = User.query.filter_by(username=form.username.data).first()

        # Check if user exists and the password is correct
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')):
            # Log the user in
            login_user(user)
            return redirect(url_for('app.home'))
        else:
            # If credentials are not valid, show an error message
            flash('Login Failed. Please check username and password', 'danger')

    return render_template('login.html', form=form)

def collect_error_messages(form_errors):
    error_messages = []
    for field_errors in form_errors.values():
        error_messages.extend(field_errors)
    return ', '.join(error_messages)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from app import db
    from models.user import User
    form = RegistrationForm()

    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), salt).decode('utf-8')

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username is already taken. Please choose a different username.')
            return redirect(url_for('auth.register'))

        # Check if the email is already taken
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email is already registered. Please use a different email address.')
            return redirect(url_for('auth.register'))

        # Create a new user
        try:
            user = User(username=form.username.data, password=hashed_password, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash('success: User registered', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"Error adding user to database: {e}")
            db.session.rollback()
    elif request.method == 'POST':
        error_messages = collect_error_messages(form.errors)
        flash(f'There were errors with your submission: {error_messages}')
        print(form.errors)

    return render_template('register.html', form=form)


@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    from models.user import User
    from app import db
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            reset_token = generate_reset_token()
            reset_token_expiration = datetime.now() + timedelta(hours=1)
            user.reset_token = reset_token
            user.reset_token_expiration = reset_token_expiration
            db.session.commit()

            send_password_reset_email(user)

            flash('success: An email with instructions to reset your password has been sent.', 'success')
        else:
            flash('Invalid username or email. Please try again.', 'danger')

        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset_password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
    from models.user import User
    from app import db
    form = ResetPasswordForm()
    user = User.query.filter_by(reset_token=reset_token).first()

    if not user or is_reset_token_expired(user.reset_token_expiration):
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.login'))

    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(form.password.data.encode(), salt)
        user.password = hashed_password.decode('utf-8')
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()

        flash('success: Your password has been successfully reset. You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', form=form, reset_token=reset_token)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('User successfully logged out.')
    return redirect(url_for('auth.login'))