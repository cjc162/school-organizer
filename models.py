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

class Projects(db.Model):
	project_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
	name = db.Column(db.String(64), nullable=False)
	project_type = db.Column(db.String(64), nullable=False)
	due_date = db.Column(db.DateTime, nullable=False)
	progress = db.Column(db.Integer, nullable=False)

	def __init__(self, user_id, name, project_type, due_date, progress):
		self.user_id = user_id
		self.name = name
		self.project_type = project_type
		self.due_date = due_date
		self.progress = progress
		

	def __repr__(self):
		return '<Project {}'.format(self.name)