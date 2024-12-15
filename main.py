import datetime
import os

import flask
from flask import Flask, render_template, request, flash
from flask_login import LoginManager, logout_user, login_required, login_user, current_user
from werkzeug.utils import redirect

from sqlalchemy import func
from data import db_sessions
from data.users import User
from data.products import Products
from data.sellers import Seller
from data.reviews import Reviews

from forms.user import LoginForm as LoginForm_user, RegisterForm as RegisterForm_user
from forms.seller import RegisterForm as RegisterForm_seller
from forms.product import AddProduct

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: int) -> User:
    """
    Возвращает нужного пользователя по его id

    Аргументы:
    user_id (int): id пользователя

    Возвращаемое значение:
    User: пользователь в виде класса User, полученный из базы данных
    """
    db_sess = db_sessions.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index() -> str:
    """
    Загружает главную страницу

    Возвращаемое значение:
    str: загружает страничку: рендерит html и возвращает строковое значение
    """
    search_query = request.args.get('search', '').strip().lower()
    db_sess = db_sessions.create_session()
    if search_query:
        products = db_sess.query(Products).filter(
            (func.lower(Products.name).contains(search_query)) |
            (func.lower(Products.description).contains(search_query))
        ).all()
    else:
        products = db_sess.query(Products).all()

    return render_template('index.html', products=products)


@app.route('/logout')
@login_required
def logout() -> flask.Response:
    """
    Загружает страницу выхода из аккаунта

    Возвращаемое значение:
    flask.Response: перебрасывает на главную страницу
    """
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login() -> str | flask.Response:
    """
    Загружает страницу входа в аккаунт

    Возвращаемое значение:
    str: загружает страничку: рендерит html и возвращает строковое значение
    flask.Response: перебрасывает на главную страницу
    """
    form = LoginForm_user()
    if form.validate_on_submit():
        db_sess = db_sessions.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister() -> str | flask.Response:
    """
    Загружает страницу регистрации в аккаунт

    Возвращаемое значение:
    str: загружает страничку: рендерит html и возвращает строковое значение
    flask.Response: перебрасывает на страницу входа в аккаунт
    """
    form = RegisterForm_user()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            flash("Пароли не совпадают", "danger")
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_sessions.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            is_seller=0,
            seller_id=-1
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/register_seller', methods=['GET', 'POST'])
def register_seller() -> str | flask.Response:
    """
    Загружает страницу регистрации пользователя как продавца

    Возвращаемое значение:
    str: загружает страничку: рендерит html и возвращает строковое значение
    flask.Response: перебрасывает на страницу продавца
    """
    form = RegisterForm_seller()
    if form.validate_on_submit():
        db_sess = db_sessions.create_session()
        if db_sess.query(Seller).filter(Seller.user_id == current_user.id).first():
            return render_template('register_seller.html', title='Регистрация продавца',
                                   form=form,
                                   message="Вы уже зарегистрированы как продавец")
        seller = Seller(
            user_id=current_user.id,
            location=form.location.data,
            score=5
        )
        db_sess.add(seller)
        db_sess.query(User).filter(User.id == current_user.id).first().seller_id = db_sess.query(Seller).filter(
            Seller.user_id == current_user.id).first().id
        db_sess.commit()
        return redirect('/seller')
    return render_template('register_seller.html', title='Регистрация продавца', form=form)


@app.route('/seller')
def seller() -> str | flask.Response:
    """
    Загружает страницу продавца

    Возвращаемое значение:
    str: загружает страничку: рендерит html и возвращает строковое значение
    flask.Response: перебрасывает на страницу регистрации пользователя как продавца
    """
    db_sess = db_sessions.create_session()
    seller_id = current_user.seller_id
    if seller_id != -1:
        products = db_sess.query(Products).filter(Products.seller_id == current_user.seller_id).all()
        return render_template("base_seller.html", products=products)
    else:
        return redirect('/register_seller')


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct() -> str | flask.Response:
    """
    Загружает страницу добавления нового продукта

    Возвращаемое значение:
    str: загружает страничку: рендерит html и возвращает строковое значение
    flask.Response: перебрасывает на страницу продавца
    """
    form = AddProduct()
    if current_user.seller_id == -1:
        return redirect('register_seller')
    if form.validate_on_submit():
        product = Products(
            seller_id=current_user.seller_id,
            name=form.product_name.data,
            description=form.description.data,
            price=form.price.data,
            image=form.image.data
        )
        db_sess = db_sessions.create_session()
        db_sess.add(product)
        db_sess.commit()
        return redirect('/seller')
    return render_template('product.html', title='Добавление товара', form=form)


@app.route('/product/<int:product_id>')
def product_detail(product_id: int) -> str | flask.Response:
    """
    Загружает страницу карточки товара

    Аргументы:
    product_id (int): id продукта

    Возвращаемое значение:
    str: загружает страничку: рендерит html и возвращает строковое значение
    flask.Response: перебрасывает на главную страницу
    """
    db_sess = db_sessions.create_session()
    product = db_sess.query(Products).filter(Products.id == product_id).first()
    reviews = db_sess.query(Reviews).filter(Reviews.product_id == product.id).all()
    if not product:
        return redirect('/')
    return render_template('product_details.html', product=product, reviews=reviews)


@app.route('/add_review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id: int) -> flask.Response:
    """
    Загружает страницу добавления отзыва о товаре

    Аргументы:
    product_id (int): id продукта

    Возвращаемое значение:
    flask.Response: перебрасывает на страницу товара
    """
    db_sess = db_sessions.create_session()
    review_text = request.form.get('review_text')
    review = Reviews(
        user_id=current_user.id,
        product_id=product_id,
        user_name=current_user.name,
        date=datetime.date.today(),
        text=review_text
    )
    db_sess.add(review)
    db_sess.commit()
    return redirect(f"/product/{product_id}")


def main():
    db_sessions.global_init('db/my_db.db')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
