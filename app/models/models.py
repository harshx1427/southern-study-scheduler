from flask_login import UserMixin
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id             = db.Column(db.Integer, primary_key=True)
    southern_email = db.Column(db.String(120), unique=True, nullable=False)
    name           = db.Column(db.String(100), nullable=False)
    password_hash  = db.Column(db.String(128), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    groups       = db.relationship("StudyGroup", backref="creator", lazy=True)
    memberships  = db.relationship("Membership", backref="user", lazy=True)
    messages     = db.relationship("Message", backref="author", lazy=True)


class StudyGroup(db.Model):
    __tablename__ = "study_groups"

    id             = db.Column(db.Integer, primary_key=True)
    subject        = db.Column(db.String(50), nullable=False)
    meet_time      = db.Column(db.DateTime, nullable=False)
    name           = db.Column(db.String(100), nullable=False)
    description    = db.Column(db.Text)
    location       = db.Column(db.String(200), nullable=False)
    created_by_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    forums      = db.relationship("Forum", backref="study_group", lazy=True)
    memberships = db.relationship("Membership", backref="study_group", lazy=True)


class Forum(db.Model):
    __tablename__ = "forums"

    id               = db.Column(db.Integer, primary_key=True)
    study_group_id   = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)
    title            = db.Column(db.String(150), nullable=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    messages = db.relationship("Message", backref="forum", lazy=True)


class Message(db.Model):
    __tablename__ = "messages"

    id         = db.Column(db.Integer, primary_key=True)
    forum_id   = db.Column(db.Integer, db.ForeignKey("forums.id"), nullable=False)
    author_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    posted_at  = db.Column(db.DateTime, default=datetime.utcnow)


class Membership(db.Model):
    __tablename__ = "memberships"

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    study_group_id = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)
    role           = db.Column(db.String(50), default="member")
    joined_at      = db.Column(db.DateTime, default=datetime.utcnow)
