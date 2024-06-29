import unittest
from website import create_app, db
from website.models import User, Quiz, Rating
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from os import environ

class FlaskTestCase(unittest.TestCase):

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
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('text/html' in response.content_type)
        self.assertTrue('QuizMania' in response.get_data(as_text=True))

class QuizTestCase(unittest.TestCase):

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

        example_quiz = Quiz(title="example", unique_id='example123', questions='[{"question": "Test?", "answers": ["Yes", "No"], "correct_answer": "Yes"}]')
        db.session.add(example_quiz)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_quiz(self):
        # Test the GET request
        response = self.client.get('/quiz')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('answers' in response.get_data(as_text=True))

    def test_post_quiz(self):
        response = self.client.post('/quiz', data={
            'unique_id': 'example123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Quiz ID not found' not in response.get_data(as_text=True))
        self.assertTrue('Test?' in response.get_data(as_text=True))

class QuizRatingTestCase(unittest.TestCase):
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
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_update_average_rating(self):
        # Create a quiz
        quiz = Quiz(title='Test Quiz', unique_id='test123', questions='[]')
        db.session.add(quiz)
        db.session.commit()

        # Add some ratings
        rating1 = Rating(quiz_id=quiz.id, user_id='user1', rating=3.5)
        rating2 = Rating(quiz_id=quiz.id, user_id='user2', rating=4.5)
        db.session.add(rating1)
        db.session.add(rating2)
        db.session.commit()

        quiz.update_average_rating()
        self.assertEqual(quiz.average_rating, 4.0)

        rating3 = Rating(quiz_id=quiz.id, user_id='user3', rating=5.0)
        db.session.add(rating3)
        db.session.commit()

        quiz.update_average_rating()
        self.assertAlmostEqual(quiz.average_rating, (3.5 + 4.5 + 5.0) / 3)


if __name__ == '__main__':
    unittest.main()