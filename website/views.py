from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from html import unescape
from .models import User, Quiz, Score, Reward, db, rewards, Rating
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

import requests
import random
import json
import pycountry

views = Blueprint("views", __name__)

def delete_score(score_id):
    score_to_delete = Score.query.get(score_id)
    if score_to_delete is not None:
        db.session.delete(score_to_delete)
        db.session.commit()
    else:
        print("Score not found")

@views.route('/')
def home():
    return render_template("index.html", user=current_user)

@views.route("/quiz/<unique_id>", methods=["GET", "POST"])
@views.route("/quiz", methods=["GET","POST"])
def quiz(unique_id=None):
    if request.method == "POST":
        replacement_question = {}
        # data = request.get_json()
        # unique_id = data['unique_id']
        unique_id = request.form.get("unique_id")
        # Check if the quiz with the unique_id exists
        quiz = Quiz.query.filter_by(unique_id=unique_id).first()
        if not quiz:
            flash("Quiz ID not found", "error")
            return redirect(url_for("views.home"))

        # Convert the questions JSON string back to a Python list
        questions = json.loads(quiz.questions)
        if len(questions) > 10:
            questions = random.sample(questions, 11)
            

        for question in questions:
            answers = question['answers']
            random.shuffle(answers)
            question['answers'] = answers
            correct_index = question['answers'].index(question['correct_answer'])
            question['correct_index'] = correct_index
            del question['correct_answer']
        print(questions)
        random.shuffle(questions)
        if len(questions) > 10:
            replacement_question = questions.pop()

        highest_score = 0
        quiz_id = unique_id
        if current_user.is_authenticated:
            user_high_score = Score.query.filter_by(user_id=current_user.username).filter_by(quiz_id=quiz_id).order_by(Score.score.desc()).first()
            if user_high_score:
                highest_score = user_high_score.score

        top_scores = Score.query.filter_by(quiz_id=quiz_id).order_by(Score.score.desc()).limit(5).all()
        
        return render_template("quiz.html", user=current_user, questions=questions, quiz_id=unique_id, highest_score=highest_score, top_scores=top_scores, is_logged_in=current_user.is_authenticated, replacement_question=replacement_question)

        
    parameters = {
        "amount": 11,
        "type": "multiple",
        "difficulty": "easy"
    }

    response = requests.get(url="https://opentdb.com/api.php", params=parameters)

    if response.status_code == 200:
        data = response.json()
        questions = []
        for item in data['results']:
            question_text = unescape(item['question'])
            correct_answer = unescape(item['correct_answer'])
            incorrect_answers = unescape(item['incorrect_answers'])
            all_answers = [correct_answer] + incorrect_answers
            random.shuffle(all_answers)
            correct_index = all_answers.index(correct_answer)
            questions.append({"question": question_text, "answers": all_answers, "correct_index": correct_index})
        if len(questions) > 10:
            replacement_question = questions.pop()

    else:
        # Handle the error
        questions = [{"question": "Error fetching question", "answers": ["Error"] * 4}] * 10

    highest_score = 0
    quiz_id = "general"
    if current_user.is_authenticated:
        user_high_score = Score.query.filter_by(user_id=current_user.username).filter_by(quiz_id=quiz_id).order_by(Score.score.desc()).first()
        if user_high_score:
            highest_score = user_high_score.score


    top_scores = Score.query.filter_by(quiz_id=quiz_id).order_by(Score.score.desc()).limit(5).all()

    return render_template("quiz.html", user=current_user, questions=questions, top_scores=top_scores, highest_score=highest_score, quiz_id=quiz_id, is_logged_in=current_user.is_authenticated, replacement_question=replacement_question)        


@views.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    current_score = request.json.get('score')
    quiz_id = request.json.get('quiz_id')

    existing_score = Score.query.filter_by(user_id=current_user.username, quiz_id=quiz_id).first()

    if existing_score:
        existing_score.update_last_three_scores(current_score)
        # If existing score is less than the current score, update it
        if existing_score.score < current_score:
            existing_score.score = current_score
            db.session.commit()
    else:
        # If no existing score, create a new score entry
        new_score = Score(user_id=current_user.username, quiz_id=quiz_id, score=current_score)
        new_score.update_last_three_scores(current_score)
        db.session.add(new_score)
        db.session.commit()

    return jsonify({'status': 'success'})

@views.route('/add_coins', methods=['POST'])
@login_required
def add_coins():
    try:
        coins_to_add = request.json.get('coins')
        if coins_to_add is None or not isinstance(coins_to_add, int):
            return jsonify({'error': 'Invalid number of coins provided'}), 400

        user = current_user
        # Update the user's coins
        user.coins += coins_to_add
        db.session.commit()
        return jsonify({'message': 'Coins successfully added', 'total_coins': user.coins}), 200

    except Exception as e:
        # If something goes wrong, roll back the transaction and return an error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@views.route('/create_quiz/<string:unique_id>', methods=['GET', 'POST'])
@views.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz(unique_id=None):
    questions = []
    if request.method == 'POST':
        data = request.get_json()
        title = data['title']
        unique_id = data['unique_id']
        description = data['description']
        questions_json = json.dumps(data.get('questions'))
        print(questions_json)
                    
        if not title or not unique_id:
            # flash('Title and unique ID are required.', 'error')
            return jsonify({'error': 'Title and unique ID are required.'}), 400
        
        existing_quiz = Quiz.query.filter_by(unique_id=unique_id).first()
        

        if existing_quiz:
            quiz_creator = existing_quiz.username
            if (current_user.username != quiz_creator):
                return jsonify({'error': 'Quiz with this ID already exists'}), 400
            else:
                existing_quiz.title = title
                existing_quiz.description = description
                existing_quiz.questions = questions_json
                db.session.commit()
        else:        
            try:
                new_quiz = Quiz(title=title, unique_id=unique_id, description=description, questions=questions_json, username=current_user.username)
                db.session.add(new_quiz)
                db.session.commit()
                flash('Quiz created successfully', 'success')
                return jsonify({'message': 'Quiz created successfully'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500
                # flash(str(e), 'error')
        
    if unique_id:
        quiz = Quiz.query.filter_by(unique_id=unique_id).first()
        if quiz:
            # Prepare the data to populate the form for editing
            questions = json.loads(quiz.questions) if quiz.questions else []
            return render_template("new_quiz.html", user=current_user, quiz=quiz, questions=questions)
        else:
            flash('Quiz not found', 'error')
            return redirect(url_for('views.my_quizzes'))
    return render_template("new_quiz.html", user=current_user, questions=questions)


@views.route('/leaderboards', methods=['GET', 'POST'])
def leaderboards():
    if request.method == 'POST':
        data = request.get_json()
        quiz_id = data.get('quizId')
        print(quiz_id)

        # When querying users for the leaderboard, use `joinedload` to load the rewards.
        top_scores = (db.session.query(Score)
                    .options(joinedload(Score.user).joinedload(User.rewards))
                    .filter(Score.quiz_id == quiz_id)
                    .order_by(Score.score.desc())
                    .limit(5)
                    .all())
        
        # print(top_scores)
        # reward_name = "hint_replace"
        # reward_title = "Replace Question"
        # reward_imageurl = "images/replaceq.png"
        # reward_coincost = 50
        # reward_type = "hint"
        # new_reward = Reward(title=reward_title, name=reward_name, image_url=reward_imageurl, coin_cost=reward_coincost, type=reward_type)
        # reward = Reward.query.filter_by(id=4).first()

        # reward.image_url = "images/50.png"
        # db.session.add(new_reward)
        # db.session.commit()
        
        # Construct the data including the reward URLs
        scores_data = []
        for score in top_scores:
            reward_url = None
            username = score.user_id
            user = User.query.filter_by(username=username).first()
            country_code = user.country_code

            if user.selected_reward:
                reward_url = user.selected_reward.image_url
            else:
                reward_url = None

            print(reward_url)    
            score_data = {
                'username': username, 
                'score': score.score,
                'rewardImageUrl': reward_url,
                'country_code': country_code
            }
            scores_data.append(score_data)

        return jsonify(scores_data)
    else:
        return render_template("leaderboards.html", user=current_user)


@views.route('/my_quizzes', methods=['GET', 'POST'])
def my_quizzes():
    return render_template("my_quizzes.html", user=current_user)

@views.route('/get-my-quizzes', methods=['GET'])
@login_required
def get_my_quizzes():
    quizzes = Quiz.query.filter_by(username=current_user.username).all()
    quizzes_data = [{
        'title': quiz.title,
        'description': quiz.description,
        'num_questions': len(json.loads(quiz.questions)), 
        'unique_id': quiz.unique_id
    } for quiz in quizzes]
    return jsonify({'quizzes': quizzes_data})

@views.route('/get-quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.order_by(Quiz.average_rating.desc()).all()
    quizzes_data = [{
        'title': quiz.title,
        'unique_id': quiz.unique_id,
        'average_rating': quiz.average_rating,
        'description': quiz.description
    } for quiz in quizzes]
    return jsonify({'quizzes': quizzes_data})

@views.route('/get-user-coins', methods=['GET'])
@login_required
def get_user_coins():
    user= User.query.filter_by(username=current_user.username).first()
    user_coins = user.coins
    print(user_coins)
    return jsonify({"coins": user_coins})

@views.route('/store', methods=['GET', 'POST'])
def store():
    rewards = Reward.query.all()
    return render_template("store.html", user=current_user, rewards=rewards)

def purchase_reward(user, reward_id):
    reward = Reward.query.filter_by(id=reward_id).first()

    if reward is None:
        return False, "Reward not found.", user.coins
    if reward.type == "badge":
        if reward in user.rewards:
            return False, "Reward already purchased.", user.coins
    if reward.name == "hint_5050":
        if (user.fifty_count or 0) >= 5:
            return False, "Maximum number of 50/50 rewards already owned."
    if reward.name == "hint_replace":
        if (user.replace_count or 0) >= 5:
            return False, "Maximum number of Replace Question rewards already owned."
    try:
        if user.coins >= reward.coin_cost:
            if reward.name == "hint_5050":
                if user.fifty_count is None:
                    user.fifty_count = 0
                user.fifty_count += 1
            if reward.name == "hint_replace":
                if user.replace_count is None:
                    user.replace_count = 0
                user.replace_count += 1
            user.coins -= reward.coin_cost
            if reward.type == "badge":
                user.rewards.append(reward)
            db.session.commit()
            return True, "Reward successfully purchased.", user.coins
        else:
            return False, "Not enough coins.", user.coins
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, f"An error occurred: {str(e)}", user.coins
    
@views.route('/buy_reward', methods=['POST'])
@login_required
def buy_reward():
    data = request.get_json()
    reward_id = data['rewardId']
    user = current_user

    success,  message, new_coin_balance = purchase_reward(user, reward_id)
    
    if success:
        return jsonify(success=True, newCoinBalance=new_coin_balance)
    else:
        return jsonify(success=False, message=message)

@views.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        country = {"name":"Select a country"}
        country_code = user.country_code
        print(country_code)
        if country_code != None:
            country = pycountry.countries.get(alpha_2=country_code)
            print(country)
        selected_reward_title = user.selected_reward.title if user.selected_reward else 'No reward selected'
        return render_template('profile.html', user=user, selected_reward_title=selected_reward_title, country=country)
    else:
        return render_template('404.html'), 404

@views.route('/update-country', methods=['POST'])
@login_required
def update_country():
    user = current_user
    data = request.json
    country_code = data.get('country_code')
    
    user.country_code = country_code
    db.session.commit()
    
    return jsonify({'status': 'success'})


@views.route('/select_reward', methods=['POST'])
@login_required
def select_reward():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'User not authenticated'}), 401
    
    data = request.get_json()
    selected_reward_id = data.get('rewardId')
    
    if selected_reward_id == '0' or selected_reward_id.lower() == 'null':
        selected_reward_id = None

    user = current_user
    try:
        # Update the user's selected reward
        user.selected_reward_id = selected_reward_id
        db.session.commit()

        # Get the reward object based on selected_reward_id
        reward = Reward.query.get(selected_reward_id)
        if reward:
            reward_url = url_for('static', filename=reward.image_url, _external=True)
        else:
            reward_url = None
        return jsonify({'success': True, 'message': 'Reward selected successfully', 'rewardUrl': reward_url})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@views.route('/use_fifty_fifty', methods=['POST'])
@login_required
def use_fifty_fifty():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'User not authenticated'}), 401
    try:
        if current_user.fifty_count > 0:
            current_user.fifty_count -= 1
            db.session.commit()
            return jsonify({'success': True, 'message': '50/50 used successfully.'})
        else:
            return jsonify({'success': False, 'message': 'No 50/50 rewards available.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred.'})
    
@views.route('/use_replacement', methods=['POST'])
@login_required
def use_replacement():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'User not authenticated'}), 401
    try:
        if current_user.replace_count > 0:
            current_user.replace_count -= 1
            db.session.commit()
            return jsonify({'success': True, 'message': 'Skip used successfully.'})
        else:
            return jsonify({'success': False, 'message': 'No Skip rewards available.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred.'})

@views.route('/check_fifty_fifty', methods=['GET'])
def check_fifty_fifty():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'User not authenticated'}), 401

    if current_user.fifty_fifty_count > 0:
        return jsonify({'success': True, 'has_fifty_fifty': True})
    else:
        return jsonify({'success': True, 'has_fifty_fifty': False})
    
@views.route('/submit_rating', methods=['POST'])
@login_required
def submit_rating():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    user_rating = data.get('rating')

    if not quiz_id or user_rating is None:
        return jsonify({"error": "Missing quiz_id or rating"}), 400

    # Check if the quiz exists
    quiz = Quiz.query.filter_by(unique_id=quiz_id).first()
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    try:
        # Use the method from the Rating model to create or update the rating
        Rating.create_or_update_rating(user_id=current_user.id, quiz_id=quiz_id, new_rating=user_rating)
        quiz.update_average_rating()
        print(quiz.average_rating)
        return jsonify({"message": "Rating submitted successfully", "average_rating": quiz.average_rating}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@views.route('/get-last-three-scores')
def get_last_three_scores_route():
    user_id = request.args.get('user_id')
    quiz_id = request.args.get('quiz_id')
    
    print(f'Received user_id: {user_id}, quiz_id: {quiz_id}')
    
    scores_object = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    
    if scores_object:
        last_three_scores = json.loads(scores_object.last_three_scores or '[]')
        return jsonify(last_three_scores)
    else:
        return jsonify([]), 404  # No score found for that user and quiz

