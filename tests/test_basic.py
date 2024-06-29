import unittest
from website import create_app, db
from website.models import User
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from os import environ

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': environ.get("SECRET_KEY")
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_main_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>QuizHome</title>', response.data)


class UserLoginTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': environ.get("SECRET_KEY")
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.user = User(email='test@example.com', username='testuser', password='testpassword')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        # Remove database session and drop all tables
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_login(self):
        # Simulate a user login
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertTrue(self.user.is_authenticated)
        self.assertEqual(response.status_code, 200)
        # Testing user starts with zero coins & zero fifty fifty hints
        self.assertEqual(self.user.coins, 0)
        self.assertEqual(self.user.fifty_count, 0)


    def test_user_logout(self):
        with self.client:
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'testpassword'
            }, follow_redirects=True)

            # User should be logged in now
            self.assertTrue(self.user.is_authenticated)
            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)


class UserSignUpTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(test_config={
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': environ.get("SECRET_KEY")
        }).test_client()
        self.app_context = self.app.application.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup_page(self):
        response = self.app.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    def test_successful_signup(self):
        response = self.app.post('/signup', data=dict(
            email='test@example.com',
            username='testuser',
            password1='TestPassword',
            password2='TestPassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user, "User was not created in the database")
        self.assertEqual(user.email, 'test@example.com', "The user email does not match the one used for signup")

    def test_signup_existing_username(self):
        # Create an existing user
        existing_user = User(username='testuser', email='test@example.com',
                             password=generate_password_hash('testpassword', method='sha256'))
        db.session.add(existing_user)
        db.session.commit()

        response = self.app.post('/signup', data=dict(
            email='other@example.com',
            username='testuser',
            password1='TestPassword',
            password2='TestPassword'
        ), follow_redirects=True)
        self.assertIn(b'Username already exists', response.data)

    def test_signup_existing_email(self):
        # Create an existing user with email
        existing_user = User(username='otheruser', email='test@example.com',
                             password=generate_password_hash('testpassword', method='sha256'))
        db.session.add(existing_user)
        db.session.commit()

        response = self.app.post('/signup', data=dict(
            email='test@example.com',
            username='newuser',
            password1='TestPassword',
            password2='TestPassword'
        ), follow_redirects=True)
        self.assertIn(b'Email already exists', response.data)

    def test_passwords_do_not_match(self):
        response = self.app.post('/signup', data=dict(
            email='test@example.com',
            username='testuser',
            password1='TestPassword',
            password2='DifferentPassword'
        ), follow_redirects=True)
        self.assertIn(b'Passwords do not match', response.data)


# runs the tests
if __name__ == "__main__":
    unittest.main()
