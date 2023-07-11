from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError
import re


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password field is required."),
        Length(min=8, message="Password should be at least 8 characters long."),
        Regexp(r'.*[A-Z].*', message="Password should contain at least one uppercase letter.")
    ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp(r'^[\w\.-]+@safeshipmoving\.com$', message='Please use a valid @safeshipmoving.com email address.')
    ])
        
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')