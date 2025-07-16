
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort

from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from online_restaurant_db import Session, Users, Menu, Orders, Reservation
from datetime import datetime

import secrets
from flask_wtf import CSRFProtect

from dotenv import load_dotenv
import os
import uuid

from forms import RegisterForm, LoginForm, AddPositionForm, AddToCartForm, OrderForm, DummyForm
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, static_folder='static', static_url_path='/static')
csrf = CSRFProtect(app)

FILES_PATH = 'static/menu'

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['UPLOAD_FOLDER'] = FILES_PATH
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['MAX_FORM_PARTS'] = 500

app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

app.config['SECRET_KEY'] = '#cv)3v7w$*s3fk;5c!@y0?:?№3"9)#'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return None
    with Session() as s:
        user = s.query(Users).filter_by(id=user_id).first()
        return user

@app.after_request
def apply_csp(response):
    nonce = secrets.token_urlsafe(16)
    csp = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; "
        f"font-src https://fonts.gstatic.com; "
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
        f"form-action 'self';"
    )
    response.headers["Content-Security-Policy"] = csp
    response.set_cookie('nonce', nonce)
    return response

@app.route('/')
@app.route('/home/')
def home():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

    return render_template('home.html')

@app.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nickname = form.nickname.data
        email = form.email.data
        password = form.password.data

        new_user = Users(nickname=nickname, email=email)
        new_user.set_password(password)

        db = Session()
        db.add(new_user)
        db.commit()
        db.close()

        return redirect(url_for("login"))

    return render_template("register.html", form=form)

@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')

        with Session() as session:
            user = session.query(Users).filter_by(nickname=nickname).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'error')

    return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))

@app.route("/add_position/", methods=['GET', 'POST'])
@login_required
def add_position():
    if current_user.nickname != 'Admin':
        return redirect(url_for('home'))

    form = AddPositionForm()
    print('FORM SUBMIT:', request.method)
    print('IS VALID:', form.validate_on_submit())
    print('FORM ERRORS:', form.errors)

    if form.validate_on_submit():
        file = form.img.data
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(FILES_PATH, filename)
        file.save(filepath)

        menu_item = Menu(
            name=form.name.data,
            weight=form.weight.data,
            ingredients=form.ingredients.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            file_name=filename
        )

        db = Session()
        db.add(menu_item)
        db.commit()
        db.close()

        flash("Menu item added successfully!", "success")
        return redirect(url_for("home"))

    return render_template('add_position.html', form=form)

@app.route('/menu/')
def menu():
    with Session() as session:
        all_positions = session.query(Menu).filter_by(active=True).all()
    return render_template('menu.html', all_positions=all_positions)

@app.route('/position/<name>', methods=['GET', 'POST'])
def position(name):
    form = AddToCartForm()

    with Session() as cursor:
        us_position = cursor.query(Menu).filter_by(active=True, name=name).first()
        if not us_position:
            abort(404)

    form.name.data = us_position.name

    if form.validate_on_submit():
        position_name = form.name.data
        position_num = form.num.data

        basket = session.get('basket', {})
        basket[position_name] = position_num
        session['basket'] = basket

        flash('Position added to the basket.', 'success')
        return redirect(url_for('position', name=position_name))

    return render_template('position.html', form=form, position=us_position)


@app.route('/basket/')
def basket():
    basket = session.get('basket', {})

    if not basket:
        flash("Your basket is currently empty.", "info")
        return redirect(url_for('menu'))

    items = []
    total = 0

    with Session() as db:
        for name, quantity in basket.items():
            position = db.query(Menu).filter_by(name=name).first()
            if position:
                subtotal = position.price * int(quantity)
                total += subtotal
                items.append({
                    'name': name,
                    'quantity': quantity,
                    'price': position.price,
                    'subtotal': subtotal,
                    'img': position.file_name
                })

    form = DummyForm()

    return render_template('basket.html', items=items, total=total, form=form)


@app.route('/create_order/', methods=['GET', 'POST'])
def create_order():
    form = OrderForm()
    basket = session.get('basket')

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("To place an order you must be registered.")
        elif not basket:
            flash("Your basket is empty.")
        else:
            with Session() as cursor:
                new_order = Orders(order_list=basket, order_time=datetime.now(), user_id=current_user.id)
                cursor.add(new_order)
                cursor.commit()
                session.pop('basket')
                cursor.refresh(new_order)
                return redirect(f"/my_order/{new_order.id}")

    return render_template('create_order.html', form=form, basket=basket)

@app.route('/clear_basket/', methods=['POST'])
def clear_basket():
    session.pop('basket', None)
    flash("Basket cleared.")
    return redirect(url_for('basket'))

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    item_name = request.form.get('item_name')
    action = request.form.get('action')

    basket = session.get('basket', {})

    warning_occurred = False

    if item_name in basket:
        if action == 'increase':
            if basket[item_name] < 8:
                basket[item_name] += 1
            else:
                flash("Cannot increase above 8", 'warning')
                warning_occurred = True
        elif action == 'decrease':
            if basket[item_name] > 1:
                basket[item_name] -= 1
            else:
                flash("Cannot decrease below 1. To remove item use 'Delete'.", 'warning')
                warning_occurred = True

        session['basket'] = basket

        if not warning_occurred:
            flash(f'Quantity updated for {item_name}', 'success')
    else:
        flash(f'{item_name} not found in basket.', 'error')

    return redirect(url_for('basket'))


@app.route('/remove_item/', methods=['POST'])
def remove_item():
    item_name = request.form.get('item_name')
    basket = session.get('basket', {})

    if item_name in basket:
        del basket[item_name]
        session['basket'] = basket
        flash(f'{item_name} removed from the basket.', 'success')
    else:
        flash(f'{item_name} not found in basket.', 'error')

    return redirect(url_for('basket'))

@app.route('/my_orders')
@login_required
def my_orders():
    with Session() as cursor:
        us_orders = cursor.query(Orders).filter_by(user_id=current_user.id).all()
    return render_template('my_orders.html', us_orders=us_orders)

@app.route("/my_order/<int:id>")
@login_required
def my_order(id):
    with Session() as cursor:
        us_order = cursor.query(Orders).filter_by(id=id).first()
        total_price = sum(int(cursor.query(Menu).filter_by(name=i).first().price) * int(cnt) for i, cnt in us_order.order_list.items())
    return render_template('my_order.html', order=us_order, total_price=total_price)


if __name__ == '__main__':
    app.run(debug=True)
