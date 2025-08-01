
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort

from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from geopy.distance import geodesic

from online_restaurant_db import Session, Users, Menu, Orders, Reservation
from datetime import datetime

import secrets
from flask_wtf import CSRFProtect

from dotenv import load_dotenv
import os
import uuid

from forms import RegisterForm, LoginForm, AddPositionForm, AddToCartForm, OrderForm, DummyForm, ReserveTableForm
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, static_folder='static', static_url_path='/static')
csrf = CSRFProtect(app)

FILES_PATH = 'static/menu'

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['UPLOAD_FOLDER'] = FILES_PATH
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MAX_FORM_PARTS'] = 500

app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

app.config['SECRET_KEY'] = '#cv)3v7w$*s3fk;5c!@y0?:?№3"9)#'

CAFE_COORDS = (38.710806, 16.118000)

RESERVATION_RADIUS_KM = 10

TABLE_NUM = {
    '1-2': 5,
    '3-4': 3,
    '4+': 2
}

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
    flash('Successfully logged out.', 'success')
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
    selected_category = request.args.get('category')

    with Session() as session:
        categories = session.query(Menu.category).distinct().all()
        categories = [c[0] for c in categories]

        if selected_category:
            all_positions = session.query(Menu).filter_by(active=True, category=selected_category).all()
        else:
            all_positions = session.query(Menu).filter_by(active=True).all()

    return render_template(
        'menu.html',
        all_positions=all_positions,
        categories=categories,
        selected_category=selected_category
    )


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

@app.route('/update_quantity/', methods=['POST'])
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

@app.route('/my_orders/')
@login_required
def my_orders():
    form = DummyForm()
    with Session() as cursor:
        us_orders = cursor.query(Orders).filter_by(user_id=current_user.id).all()
    return render_template('my_orders.html', us_orders=us_orders, form=form)

@app.route("/my_order/<int:id>")
@login_required
def my_order(id):
    form = DummyForm()
    with Session() as cursor:
        us_order = cursor.query(Orders).filter_by(id=id).first()
        total_price = sum(
            cursor.query(Menu).filter_by(name=i).first().price * int(cnt)
            for i, cnt in us_order.order_list.items()
        )
    return render_template('my_order.html', order=us_order, total_price=total_price, form=form)

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    form = DummyForm()
    if form.validate_on_submit():
        with Session() as db:
            order = db.query(Orders).filter_by(id=order_id, user_id=current_user.id).first()
            if not order:
                abort(404)
            db.delete(order)
            db.commit()
        flash("Order cancelled.", "info")
    else:
        flash("Invalid form submission.", "danger")
    return redirect(url_for('my_orders'))

@app.route('/reserved/', methods=['GET', 'POST'])
@login_required
def reserved():
    form = ReserveTableForm()
    message = ''

    if form.validate_on_submit():
        table_type = form.table_type.data
        reserved_time_start = form.time.data
        user_latitude = form.latitude.data
        user_longitude = form.longitude.data

        if not user_longitude or not user_latitude:
            flash('You have not provided your location information.', 'warning')
        else:
            user_cords = (float(user_latitude), float(user_longitude))
            distance = geodesic(CAFE_COORDS, user_cords).km
            if distance > RESERVATION_RADIUS_KM:
                flash("You are in an area not available for booking.", 'danger')
            else:
                with Session() as cursor:
                    reserved_check = cursor.query(Reservation).filter_by(type_table=table_type).count()
                    user_reserved_check = cursor.query(Reservation).filter_by(user_id=current_user.id).first()

                    if reserved_check < TABLE_NUM.get(table_type) and not user_reserved_check:
                        new_reserved = Reservation(type_table=table_type, time_start=reserved_time_start, user_id=current_user.id)
                        cursor.add(new_reserved)
                        cursor.commit()
                        flash(f'Reservation for {reserved_time_start} table for {table_type} people has been successfully created.', 'success')
                    elif user_reserved_check:
                        flash('You can only have one active reservation.', 'info')
                    else:
                        flash('Unfortunately, this type of table is currently not available for reservation.', 'warning')

    return render_template('reserved.html', form=form)

@app.route('/reservations_check/', methods=['GET', 'POST'])
@login_required
def reservations_check():
    form = DummyForm()
    if current_user.nickname != 'Admin':
        return redirect(url_for('home'))

    if request.method == "POST":

        reserv_id = request.form['reserv_id']
        with Session() as cursor:
            reservation = cursor.query(Reservation).filter_by(id=reserv_id).first()
            cursor.delete(reservation)
            cursor.commit()

    with Session() as cursor:
        all_reservations = cursor.query(Reservation).all()
        return render_template('reservations_check.html', all_reservations=all_reservations, form=form)

@app.route('/menu_check/', methods=['GET', 'POST'])
@login_required
def menu_check():
    form = DummyForm()
    if current_user.nickname != 'Admin':
        return redirect(url_for('home'))

    if request.method == 'POST':

        position_id = request.form['pos_id']
        with Session() as cursor:
            position_obj = cursor.query(Menu).filter_by(id=position_id).first()
            if 'change_status' in request.form:
                position_obj.active = not position_obj.active
            elif 'delete_position' in request.form:
                cursor.delete(position_obj)
            cursor.commit()

    with Session() as cursor:
        all_positions = cursor.query(Menu).all()
    return render_template('check_menu.html', all_positions=all_positions, csrf_token=session["csrf_token"], form=form)

@app.route('/all_users/')
@login_required
def all_users():
    if current_user.nickname != 'Admin':
        return redirect(url_for('home'))

    with Session() as cursor:
        all_users = cursor.query(Users).with_entities(Users.id, Users.nickname, Users.email).all()
    return render_template('all_users.html', all_users=all_users)


if __name__ == '__main__':
    app.run(debug=True)
