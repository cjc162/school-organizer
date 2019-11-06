import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import select
from sqlalchemy.sql.functions import func
from werkzeug import check_password_hash, generate_password_hash

from models import db, User, Assignments

app = Flask(__name__)

SECRET_KEY = 'development key'

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'organizer.db')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

app.config.from_object(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	db.create_all()

	print('Initialized the database.')

def get_user_id(username):
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

def get_event_id(date):
	rv = Event.query.filter_by(date=date).first()
	return rv.event_id if rv else None

def get_date_object(date):
	split_date = date.split("-")

	if(len(split_date) != 3):
		return None
	else:
		return datetime(int(split_date[0]), int(split_date[1]), int(split_date[2]))

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()

@app.route('/')
def index():
	if g.user:
		return redirect(url_for('assignments'))
	else:
		return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	# If user is logged in, redirect them to index
	if g.user:
		return redirect(url_for('index'))
	error = None

	# If the user posts (submits)
	if request.method == 'POST':
		# See if username entered is registered
		user = User.query.filter_by(username=request.form['username']).first()
		# If usernmame is not registered, display error
		if user is None:
			error = 'Invalid username'
		# If password for the user is not correct, display error
		elif not check_password_hash(user.pw_hash, request.form['password']):
			error = 'Invalid password'
		# A correct username and password is entered, redirect them to the correct page
		else:
			flash('You were logged in')
			session['user_id'] = user.user_id
			return redirect(url_for('assignments'))
	return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
	# If user is logged in
	if g.user:
		return redirect(url_for('index'))
	error = None
	# If user posts (submits)
	if request.method == 'POST':
		# Check username is not empty
		if not request.form['username']:
			error = 'You have to enter a username'
		# Check password is not empty
		elif not request.form['password']:
			error = 'You have to enter a password'
		# Check both passwords match
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		# Check if username is already taken
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		# User successfully registered
		else:
			db.session.add(User(request.form['username'], generate_password_hash(request.form['password'])))
			db.session.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

@app.route('/logout')
def logout():
	flash('You were logged out')
	# Log out user
	session.pop('user_id', None)
	return redirect(url_for('index')) 

@app.route('/assignments')
def assignments():
	# If user is not logged in
	if not g.user:
		return redirect(url_for('index'))

	# Get all events the current user has created
	assignments = Assignments.query.filter_by(user_id=g.user.user_id).order_by(Assignments.due_date.asc()).all()	

	return render_template('assignments.html', assignments = assignments)

@app.route('/add_assignments', methods=['GET', 'POST'])
def add_assignments():
	# If user is not logged in
	if not g.user:
		return redirect(url_for('index'))
	error = None
	# If user posts (submits)
	if request.method == 'POST':
		# Check name is not empty
		if not request.form['name']:
			error = 'You have to enter an assignment name'
		# Check date is not empty
		elif not request.form['date']:
			error = 'You have to enter a due date'
		# Assignment successfully created
		else:
			date = get_date_object(request.form['date'])

			db.session.add(Assignments(session['user_id'], request.form['name'], request.form['type'], date))
			db.session.commit()

			flash(request.form['name'] + ' successfully created')

			return redirect(url_for('assignments'))
	return render_template('add_assignments.html', error=error)

@app.route('/delete_assignment/<int:id>')
def delete_assignment(id):
	if not g.user:
		return redirect(url_for('index'))

	assignment_to_delete = Assignments.query.filter_by(user_id=g.user.user_id, assignment_id=id).first()

	if (assignment_to_delete is None):
		abort(404)

	db.session.delete(assignment_to_delete)
	db.session.commit()
	flash('Assignment successfully deleted')

	return redirect(url_for('index'))

@app.route('/update_progress/<int:id>', methods=['GET', 'POST'])
def update_progress(id):
	if not g.user:
		return redirect(url_for('index'))

	assignment_to_update = Assignments.query.filter_by(user_id=g.user.user_id, assignment_id=id).first()

	if (assignment_to_update is None):
		abort(404)
	error = None
	if request.method == 'POST':
		# Check progress is not empty
		if not request.form['progress']:
			error = 'You have to enter an update progress'
		# Progress successfully updated
		else:
			assignment_to_update.progress = request.form['progress']
			db.session.commit()

			flash(assignment_to_update.name + "'s progress successfully updated")

			return redirect(url_for('assignments'))
	return render_template('update_progress.html', error=error, assignment_name=assignment_to_update.name, id=id)


@app.route('/calendar_view', methods=['GET', 'POST'])
def calendar_view():
	# If user is not logged in
	if not g.user:
		return redirect(url_for('index'))

	# Get all events the current user has created
	assignments = Assignments.query.filter_by(user_id=g.user.user_id).order_by(Assignments.due_date.asc()).all()	

	data = []
	for assignment in assignments:
		data_dict = {}
		data_dict["day"] = str(assignment.due_date.date()).split("-")[2]
		data_dict["month"] = str(assignment.due_date.date()).split("-")[1]
		data_dict["year"] = str(assignment.due_date.date()).split("-")[0]
		data_dict["eventName"] = assignment.name
		data_dict["calendar"] = assignment.assignment_type

		if (data_dict["calendar"] == "Exam"):
			data_dict["color"] = "orange"
		elif (data_dict["calendar"] == "Project"):
			data_dict["color"] = "blue"
		elif (data_dict["calendar"] == "Homework"):
			data_dict["color"] = "yellow"
		else:
			data_dict["color"] = "green"

		data.append(data_dict)

	print(data)

	return render_template('calendar_view.html', data=data)







