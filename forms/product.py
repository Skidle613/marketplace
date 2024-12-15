from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField, BooleanField, SubmitField, StringField, TextAreaField, IntegerField, DateField, FloatField, FileField, URLField
from wtforms.validators import DataRequired


class AddProduct(FlaskForm):
    product_name = StringField('Название продукта', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired()])
    image = URLField('URl изображения', validators=[DataRequired()])
    submit = SubmitField('Создать')
