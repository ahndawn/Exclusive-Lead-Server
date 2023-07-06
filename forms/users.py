from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError
import re


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'[A-Z]')
    ])

    def validate_password(form, field):
        if len(field.data) < 8:
            flash('Password should be at least 8 characters long')
            raise ValidationError()

    def validate_password(form, field):
        if not re.search(r'[A-Z]', field.data):
            flash('Password should contain at least one capital letter')
            raise ValidationError()
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp(r'^[\w\.-]+@safeshipmoving\.com$')
    ])
    def validate_email(form, field):
        if not re.search(r'^[\w\.-]+@safeshipmoving\.com$', field.data):
            flash('Please use a valid @safeshipmoving.com email address.')
            raise ValidationError()
        
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')