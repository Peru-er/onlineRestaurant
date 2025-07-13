
from flask import Flask, render_template, request, redirect, url_for, flash, session

from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from online_restaurant_db import Session, Users, Menu, Orders, Reservation
from datetime import datetime

import secrets
from flask_wtf import CSRFProtect

import os
import uuid

from forms import RegisterForm, LoginForm, AddPositionForm
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, static_folder='static', static_url_path='/static')
csrf = CSRFProtect(app)

FILES_PATH = 'static/menu'

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
            file_name=filename
        )

        db = Session()
        db.add(menu_item)
        db.commit()
        db.close()

        flash("Menu item added successfully!", "success")
        return redirect(url_for("home"))

    return render_template('add_position.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
