from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.models import StudyGroup, Forum, ThreadMessage, Membership
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

threads_bp = Blueprint('threads', __name__, template_folder='templates')

# Form to start a new thread
class NewThreadForm(FlaskForm):
    title = StringField("Thread Title", validators=[DataRequired(), Length(max=150)])
    content = TextAreaField("Initial Message", validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField("Create Thread")

# Form to reply in an existing thread
class ThreadReplyForm(FlaskForm):
    content = TextAreaField("Your Reply", validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField("Post Reply")

@threads_bp.route('/groups/<int:group_id>/threads/new', methods=['GET','POST'])
@login_required
def new_thread(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    # ensure user is a member
    if not Membership.query.filter_by(user_id=current_user.id, study_group_id=group.id).first():
        abort(403)
    form = NewThreadForm()
    if form.validate_on_submit():
        thread = Forum(study_group_id=group.id, title=form.title.data)
        db.session.add(thread)
        db.session.commit()
        msg = ThreadMessage(thread_id=thread.id, author_id=current_user.id, content=form.content.data)
        db.session.add(msg)
        db.session.commit()
        flash("Thread created!", "success")
        return redirect(url_for('threads.view_thread', group_id=group.id, thread_id=thread.id))
    return render_template('new_thread.html', form=form, group=group)

@threads_bp.route('/groups/<int:group_id>/threads/<int:thread_id>', methods=['GET','POST'])
@login_required
def view_thread(group_id, thread_id):
    group = StudyGroup.query.get_or_404(group_id)
    thread = Forum.query.get_or_404(thread_id)
    # ensure user is a member
    if not Membership.query.filter_by(user_id=current_user.id, study_group_id=group.id).first():
        abort(403)
    form = ThreadReplyForm()
    if form.validate_on_submit():
        reply = ThreadMessage(thread_id=thread.id, author_id=current_user.id, content=form.content.data)
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('threads.view_thread', group_id=group.id, thread_id=thread.id))
    messages = thread.messages
    return render_template('view_thread.html', group=group, thread=thread, messages=messages, form=form)

@threads_bp.route('/groups/<int:group_id>/threads/<int:thread_id>/delete', methods=['POST'])
@login_required
def delete_thread(group_id, thread_id):
    thread = Forum.query.get_or_404(thread_id)
    if thread.created_by_id != current_user.id:
        abort(403)
    db.session.delete(thread)
    db.session.commit()
    flash('Thread deleted.', 'success')
    return redirect(url_for('main.view_group', group_id=group_id))