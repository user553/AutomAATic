from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField


class LoginForm(FlaskForm):
    email = StringField()
    password = PasswordField()
    login_captcha = StringField()
    submit = SubmitField('Login')
