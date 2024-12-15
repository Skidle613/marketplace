import unittest
from flask import url_for
from main import app
from data.db_sessions import global_init, create_session
from data.users import User
from data.products import Products


class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SERVER_NAME'] = 'localhost'
        self.client = self.app.test_client()

        global_init(':memory:')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.create_test_data()

    def tearDown(self):
        with self.app.app_context():
            db_sess = create_session()
            db_sess.close()

    def create_test_data(self):
        db_sess = create_session()
        user = User(
            surname='test',
            name='test',
            email='test@example.com',
            is_seller=1,
            seller_id=1
        )
        user.set_password("password")
        db_sess.add(user)
        db_sess.commit()

    def login_as_test_user(self):
        with self.client:
            self.client.post(url_for('login'), data={
                'email': 'test@example.com',
                'password': 'password'
            })

    def test_index_route(self):
        response = self.client.get(url_for('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Поиск', response.data.decode('utf-8'))

    def test_registration_failure(self):
        response = self.client.post(url_for('reqister'), data={
            'email': 'newuser@example.com',
            'password': 'password1',
            'password_again': 'password2',
            'name': 'Test',
            'surname': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Пароли не совпадают', response.data.decode('utf-8'))

    def test_add_product(self):
        self.login_as_test_user()
        response = self.client.post(url_for('addproduct'), data={
            'product_name': 'Test Product',
            'price': 100.0,
            'description': 'This is a test product.',
            'image': 'test_image.jpg'
        })
        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            db_sess = create_session()
            product = db_sess.query(Products).filter_by(name='Test Product').first()
            self.assertIsNotNone(product)
            self.assertEqual(product.price, 100.0)


if __name__ == '__main__':
    unittest.main()
