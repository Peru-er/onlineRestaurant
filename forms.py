
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, FileField, IntegerField, HiddenField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange


class RegisterForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddPositionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    img = FileField('Image', validators=[DataRequired()])
    ingredients = StringField('Ingredients', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    weight = FloatField('Weight', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Add')

class AddToCartForm(FlaskForm):
    name = HiddenField(validators=[DataRequired()])
    num = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add')

class OrderForm(FlaskForm):
    submit = SubmitField('Place Order')

class DummyForm(FlaskForm):
    pass

class ReserveTableForm(FlaskForm):
    table_type = SelectField('Table Type', choices=[
        ('1-2', '1-2 people'),
        ('3-4', '3-4 people'),
        ('4+', 'More than 4 people')
    ], validators=[DataRequired()])
    time = DateTimeLocalField('Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    submit = SubmitField('Reserve')
