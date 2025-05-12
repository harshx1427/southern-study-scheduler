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
from flask import jsonify
from sqlalchemy import func

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
        if User.query.filter_by(southern_email=form.southern_email.data).first():
            flash("This email is already in use.", "warning")
            # re‑render the form with that flash; no HTML changes needed
            return render_template('register.html', form=form)
        
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

        flash('Your account has been created! Please log In.', 'success_create')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success_logout')
    return redirect(url_for('main.index'))




class MessageForm(FlaskForm):
    recipient = StringField('Send to (email or name)', validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send')

@auth_bp.route('/message', methods=['GET', 'POST'])
@login_required
def message():
    form = MessageForm()
    user_q = request.args.get('user_q', '').strip()
    search_results = []

    # 📨 Get recent conversation partners
    partner_ids = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id) \
        .union(db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)) \
        .all()
    recent_ids = [id for (id,) in partner_ids]

    # Create dict: {user: unread_message_count}
    recent_contacts = []
    for user in User.query.filter(User.id.in_(recent_ids)).all():
        unread = Message.query.filter_by(
            sender_id=user.id,
            receiver_id=current_user.id,
            is_read=False
        ).count()
        recent_contacts.append((user, unread))

    # 🔎 Search logic
    if len(user_q) >= 2:
        search_results = User.query.filter(
            (User.name.ilike(f"{user_q}%")) |
            (User.southern_email.ilike(f"{user_q}%"))
        ).limit(10).all()

    # ✉️ Handle message sending
    if request.method == 'POST' and form.validate_on_submit():
        recipient_id = request.form.get('recipient_id')
        recipient = User.query.get(int(recipient_id))
        if recipient:
            new_msg = Message(
                sender_id=current_user.id,
                receiver_id=recipient.id,
                content=form.content.data,
                is_read=False
            )
            db.session.add(new_msg)
            db.session.commit()
            flash('Your message was sent!', 'success')
            return redirect(url_for('auth.message'))

    # 📩 Your sent messages
    messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.posted_at.desc()).all()

    # 🔴 Count total unread messages
    unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()

    return render_template(
        'message.html',
        form=form,
        messages=messages,
        search_results=search_results,
        user_q=user_q,
        recent_contacts=recent_contacts,  # now list of tuples: (User, unread_count)
        unread_count=unread_count
    )

@auth_bp.route('/api/user_suggestions')
@login_required
def user_suggestions():
    term = request.args.get('q', '').strip()
    if len(term) < 2:
        return jsonify([])

    users = User.query.filter(
        (User.name.ilike(f"{term}%")) |
        (User.southern_email.ilike(f"{term}%"))
    ).limit(5).all()

    return jsonify([{'id': u.id, 'name': u.name, 'email': u.southern_email} for u in users])


class DirectMessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send')

@auth_bp.route('/message/<int:user_id>', methods=['GET', 'POST'])
@login_required
def message_user(user_id):
    recipient = User.query.get_or_404(user_id)
    form = DirectMessageForm()

    # ✅ Mark unread messages from this user as read
    Message.query.filter_by(
        sender_id=recipient.id,
        receiver_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()

    # ✅ Always compute this before rendering template
    unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()

    if form.validate_on_submit():
        msg = Message(
            sender_id=current_user.id,
            receiver_id=recipient.id,
            content=form.content.data,
            is_read=False
        )
        db.session.add(msg)
        db.session.commit()
        flash(f'Message sent to {recipient.name}!', 'success')
        return redirect(url_for('auth.message_user', user_id=user_id))

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == recipient.id)) |
        ((Message.sender_id == recipient.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.posted_at.asc()).all()

    return render_template(
        'message_user.html',
        form=form,
        recipient=recipient,
        messages=messages,
        unread_count=unread_count
    )
