from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from app import db
from app.models.models import StudyGroup

class StudyGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
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

    return render_template('dashboard.html', name=current_user.name, groups=groups, q=q)

# New route to create a study group

@main_bp.route('/groups/new', methods=['GET', 'POST'])
@login_required
def create_group():
    form = StudyGroupForm()
    if form.validate_on_submit():
        new_group = StudyGroup(
            name=form.name.data,
            description=form.description.data,
            created_by_id=current_user.id
        )
        db.session.add(new_group)
        db.session.commit()
        flash('Study group created successfully!', 'group_success')
        return redirect(url_for('main.dashboard'))
    return render_template('create_group.html', form=form)

@main_bp.route('/groups/<int:group_id>')
@login_required
def view_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    return render_template('view_group.html', group=group)