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
    forums      = db.relationship("Forum", backref="study_group", lazy=True, cascade="all, delete-orphan")
    memberships = db.relationship("Membership", backref="study_group", lazy=True, cascade="all, delete-orphan")


class Forum(db.Model):
    __tablename__ = "forums"

    id               = db.Column(db.Integer, primary_key=True)
    study_group_id   = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)
    title            = db.Column(db.String(150), nullable=False)
    created_by_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    messages = db.relationship("ThreadMessage", backref="thread", lazy=True, cascade="all, delete-orphan")
    creator = db.relationship("User", backref="forums", foreign_keys=[created_by_id])

class ThreadMessage(db.Model):
    __tablename__ = "thread_messages"

    id         = db.Column(db.Integer, primary_key=True)
    thread_id   = db.Column(db.Integer, db.ForeignKey("forums.id"), nullable=False)
    author_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    author = db.relationship("User", backref="thread_messages")


'''class Message(db.Model):
    __tablename__ = "messages"

    message_id       = db.Column(db.Integer, primary_key=True)
    sender_user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    listing_id       = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)
    content          = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    sender   = db.relationship("User", foreign_keys=[sender_user_id], backref="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_user_id], backref="received_messages")
    listing = db.relationship("StudyGroup", backref="messages")'''

class Membership(db.Model):
    __tablename__ = "memberships"

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    study_group_id = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)
    role           = db.Column(db.String(50), default="member")
    joined_at      = db.Column(db.DateTime, default=datetime.utcnow)

    