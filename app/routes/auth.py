from flask import Blueprint, app, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from app import db
from app.models.models import User, Message
from app.routes.main import main_bp
from wtforms import SelectField

auth_bp = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    southern_email = StringField('Southern Email', validators=[DataRequired(), Length(max=120), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # So line 22-23. Flask sees that you're already logged in, so it immediately redirects you to /dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(southern_email=form.southern_email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)


class RegistrationForm(FlaskForm):
    southern_email = StringField('Southern Email', validators=[DataRequired(), Length(max=120), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            southern_email=form.southern_email.data,
            name=form.name.data,
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        # This will be the message the app send, when user register
        '''send_email(
            subject='Welcome to Study Group Finder!',
            recipients=[form.southern_email.data],
            body='Thanks for registering. You can now log in and join study groups!'
        )'''

        flash('Your account has been created! Please log In.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


class MessageForm(FlaskForm):
    recipient_id = SelectField('Send to', coerce=int)
    content = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send')


@auth_bp.route('/message', methods=['GET', 'POST'])
@login_required
def message():
    form = MessageForm()

    users = User.query.filter(User.id != current_user.id).all()
    form.recipient_id.choices = [(user.id, user.name) for user in users]

    if form.validate_on_submit():
        recipient_id = form.recipient_id.data
        content = form.content.data
        new_msg = Message(sender_id=current_user.id, receiver_id=recipient_id, content=content)
        db.session.add(new_msg)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('auth.message'))

    all_messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.posted_at.desc()).all()
    return render_template('message.html', form=form, messages=all_messages)


@auth_bp.route('/message/<int:user_id>', methods=['GET', 'POST'])
@login_required
def message_user(user_id):
    recipient = User.query.get_or_404(user_id)
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(
            sender_id=current_user.id,
            receiver_id=recipient.id,
            content=form.content.data
        )
        db.session.add(msg)
        db.session.commit()
        flash(f'Message sent to {recipient.name}!', 'success')
        return redirect(url_for('auth.message_user', user_id=user_id))
    return render_template('message_user.html', form=form, recipient=recipient)
