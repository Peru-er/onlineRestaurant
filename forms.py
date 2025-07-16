
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, FileField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange

class RegisterForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo

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

