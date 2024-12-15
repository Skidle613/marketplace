from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField, BooleanField, SubmitField, StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    location = StringField('Местоположение', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться как продавец')
