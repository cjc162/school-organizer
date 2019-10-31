from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	pw_hash = db.Column(db.String(64), nullable=False)
	
	def __init__(self, username, pw_hash):
		self.username = username
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Assignments(db.Model):
	assignment_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
	name = db.Column(db.String(64), nullable=False)
	assignment_type = db.Column(db.String(64), nullable=False)
	due_date = db.Column(db.DateTime, nullable=False)
	progress = db.Column(db.Integer, nullable=False)

	def __init__(self, user_id, name, assignment_type, due_date):
		self.user_id = user_id
		self.name = name
		self.assignment_type = assignment_type
		self.due_date = due_date
		self.progress = 0
		

	def __repr__(self):
		return '<Assignment {}'.format(self.name)