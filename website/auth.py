from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
from dotenv import load_dotenv
from os import environ

load_dotenv()
auth = Blueprint("auth", __name__)

s = URLSafeTimedSerializer(environ.get('SECRET_KEY'))

@auth.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect Password!", category="error")
        else:
            flash("Username does not exist", category="error")

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

@auth.route('/signup', methods=["GET","POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(username=username).first()
        usermail = User.query.filter_by(email=email).first()

        if user:
            flash("Username already exists", category="error")
        elif (len(username) > 15):
            flash("Username too long. The limit is 15 characters.", category="error")
        elif usermail:
            flash("Email already exists", category="error")
        elif password1 != password2:
            flash("Passwords do not match!", category="error")
        else: 
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Success", category="success")
            return redirect(url_for("views.home"))


    return render_template("signup.html", user=current_user)

@auth.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='reset-password-salt')
            msg = Message('Password Reset Request', sender=environ.get("MAIL_USERNAME"), recipients=[email])
            link = url_for('auth.reset', token=token, _external=True)
            msg.body = f'Your link to reset your password is {link}'
            mail.send(msg)
            flash('Please check your email for the password reset link.', category='success')
        else:
            flash('That email does not exist in our system.', category='error')
    return render_template('reset_request.html')

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    try:
        email = s.loads(token, salt='reset-password-salt', max_age=3600)
    except:
        flash('That reset link is invalid or has expired.', category='error')
        return redirect(url_for('auth.reset_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        user.password = generate_password_hash(password, method='sha256')
        db.session.commit()
        flash('Your password has been updated!', category='success')
        return redirect(url_for('auth.login'))

    return render_template('reset.html', token=token)