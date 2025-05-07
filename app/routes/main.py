from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length
from app import db
from app.models.models import StudyGroup, Membership

class StudyGroupForm(FlaskForm):
    subject = StringField('Course/Subject', validators=[DataRequired(),Length(max=50)])
    meet_time = DateTimeField('Meeting Date & Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    location = StringField('Location or Link', validators=[DataRequired(), Length(max=200)])
    name = StringField('Group Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Create Group')


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    q = request.args.get('q', '').strip()

    if q:
        groups = StudyGroup.query.filter(
            StudyGroup.name.ilike(f'%{q}%')
        ).all()

    else: 
        groups = StudyGroup.query.all()

    member_records = Membership.query.filter_by(user_id=current_user.id).all()
    member_group_ids = {m.study_group_id for m in member_records}

    return render_template('dashboard.html', name=current_user.name, groups=groups, q=q, member_group_ids=member_group_ids)

# New route to create a study group

@main_bp.route('/groups/new', methods=['GET', 'POST'])
@login_required
def create_group():
    form = StudyGroupForm()
    if form.validate_on_submit():
        group = StudyGroup(
            subject = form.subject.data,
            meet_time = form.meet_time.data,
            location = form.location.data,
            name=form.name.data,
            description=form.description.data,
            created_by_id=current_user.id
        )
        db.session.add(group)
        db.session.commit()
        flash('Study group created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('create_group.html', form=form)

@main_bp.route('/groups/<int:group_id>')
@login_required
def view_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    membership = Membership.query.filter_by(
        user_id=current_user.id,
        study_group_id=group.id
    ).first()
    is_member = membership is not None
    
    return render_template('view_group.html', group=group, is_member=is_member)


# Route to join a study group
@main_bp.route('/groups/<int:group_id>/join', methods=['POST'])
@login_required
def join_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    new_membership = Membership(
        user_id=current_user.id,
        study_group_id=group.id
    )
    db.session.add(new_membership)
    try:
        db.session.commit()
        flash(f'You joined"{group.name}"', 'success')
    except:
        db.session.rollback()
        flash('Could not join (already a member?)', 'warning')
    return redirect(url_for('main.dashboard'))


# Route to leave a study group
@main_bp.route('/groups/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    membership = Membership.query.filter_by(
        user_id=current_user.id,
        study_group_id=group_id
    ).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()
        flash('You left the group', 'success')
    else:
        flash('You are not a member of this group', 'warning')
    return redirect(url_for('main.dashboard'))