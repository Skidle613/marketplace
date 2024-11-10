from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField, BooleanField, SubmitField, StringField, TextAreaField, IntegerField, DateField, FloatField
from wtforms.validators import DataRequired


class AddProduct(FlaskForm):
    product_name = StringField('Название продукты', validators=[DataRequired()])
    # team_leader = StringField('Ответственнный за выполнение работы', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired()])
    submit = SubmitField('Создать')
