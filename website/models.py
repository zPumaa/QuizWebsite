from flask_login import UserMixin
import json
from . import db

rewards = db.Table('user_rewards',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('reward_id', db.Integer, db.ForeignKey('reward.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(30), unique=True)
    coins = db.Column(db.Integer, default=0)
    scores = db.relationship('Score', back_populates='user')
    rewards = db.relationship('Reward', secondary=rewards, lazy='subquery', backref=db.backref('users', lazy=True))
    selected_reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=True)
    selected_reward = db.relationship('Reward', foreign_keys=[selected_reward_id])
    fifty_count = db.Column(db.Integer, default=0)
    replace_count = db.Column(db.Integer, default=0)
    country_code = db.Column(db.String(5))
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    image_url = db.Column(db.String(255))  
    coin_cost = db.Column(db.Integer)  
    title = db.Column(db.String(50))  
    type = db.Column(db.String(50))   
    
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.String(50), db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer)
    last_three_scores = db.Column(db.String(255))

    user = db.relationship('User', back_populates='scores')
    quiz = db.relationship('Quiz', back_populates='scores')

    def update_last_three_scores(self, new_score):
        scores = json.loads(self.last_three_scores or '[]')
        
        scores.append(new_score)
        scores = scores[-3:]

        self.last_three_scores = json.dumps(scores)
        db.session.commit()

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    questions = db.Column(db.Text, nullable=False)  # Store questions as a JSON string
    scores = db.relationship('Score', back_populates='quiz')
    username = db.Column(db.String(30))
    average_rating = db.Column(db.Float, default=0)
    ratings = db.relationship('Rating', backref='quiz', lazy='dynamic')
    description = db.Column(db.String(200))

    def update_average_rating(self):
        total_ratings = Rating.query.filter_by(quiz_id=self.unique_id).count()
        print(total_ratings)
        if total_ratings > 0:
            total_score = db.session.query(db.func.sum(Rating.rating)).filter(Rating.quiz_id == self.unique_id).scalar()
            self.average_rating = total_score / total_ratings
        else:
            self.average_rating = 0
        db.session.commit()

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    # Unique constraint to ensure a user can rate a quiz only once
    __table_args__ = (db.UniqueConstraint('user_id', 'quiz_id', name='_user_quiz_uc'),)

    @classmethod
    def create_or_update_rating(cls, user_id, quiz_id, new_rating):
        rating_instance = cls.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
        if rating_instance:
            rating_instance.rating = new_rating
        else:
            rating_instance = cls(user_id=user_id, quiz_id=quiz_id, rating=new_rating)
            db.session.add(rating_instance)
        db.session.commit()
        return rating_instance



    

