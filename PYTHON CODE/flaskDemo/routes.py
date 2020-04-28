import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, AssignForm,AssignUpdateForm
from flaskDemo.models import User, Post, medicaldevices, bed, patient, doctor, assignment
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route("/")
@app.route("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(accountname=form.accountname.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check account name and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/home")
def home():
	results = patient.query.all()
	return render_template('assign_home.html', outString = results)
	results1 = doctor.query.all()
	return render_template('assign_home.html', outString1 = results1)
	posts = Post.query.all()
	return render_template('home.html', posts=posts)
	results3 = assignment.query.all()
	results2 = patient.query.join(assignment,patient.patientID == assignment.patientID) \
			   .add_columns(patient.fname, patient.lname, patient.ssn, assignment.adminID) \
			   .join(doctor, doctor.docID == assignment.docID).add_columns(doctor.docfname,doctor.doclname)
	results = patient.query.join(assignment,patient.patientID == assignment.patientID) \
			   .add_columns(patient.fname, patient.lname, patient.ssn, assignment.adminID)
	return render_template('home.html', title='Join',joined_1_n=results, joined_m_n=results2)

   


@app.route("/about")
def about():
	return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(accountname=form.accountname.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account',
						   image_file=image_file, form=form)


@app.route("/assign/new", methods=['GET', 'POST'])
@login_required
def new_assign():
	form = AssignForm()
	if form.validate_on_submit():
		assign = patient(patfname=form.patfname.data, patlname=form.patlname.data, pid=form.pid.data)
		assign1 = doctor(docid=form.docid.data)
		assign2 = assignment(docid=form.docid.data, pid=form.pid.data)
		db.session.add(assign)
		db.session.add(assign1)
		db.session.add(assign2)
		db.session.commit()
		flash('You have added a new patient!', 'success')
		return redirect(url_for('home'))
	return render_template('create_assign.html', title='New Assignment',
						   form=form, legend='New Assignment')


@app.route("/assign/<docid>/<pid>")
@login_required
def assign(docid, pid):
   assign = patient.query.get_or_404([docid,pid])
   return render_template('assign.html', title=str(assign.pid) + "_" + str(assign1.docid), assign=assign, now=datetime.utcnow())


@app.route("/assign/<docid>/<pid>update", methods=['GET', 'POST'])
@login_required
def update_assign(docid, pid):
	assign = patient.query.get_or_404([docid, pid])
	currentAssign = assign.medcondition
	form = AssignUpdateForm()
	if form.validate_on_submit():		   # notice we are are not passing the dnumber from the form
		if currentAssign !=form.medcondition.data:
			assign.medcondition=form.medcondition.data
		assign.pid=form.pid.data
		db.session.commit()
		flash('Your assignment has been updated!', 'success')
		return redirect(url_for('assign', pid=pid))
	elif request.method == 'GET':			   # notice we are not passing the dnumber to the form

		form.pid.data = assign.pid
		form.medcondition.data = assign.medcondition
	return render_template('create_assign.html', title='Update Assignment',
						   form=form, legend='Update Assignment')



@app.route("/assign/<docid>/<pid>delete", methods=['POST'])
@login_required
def delete_assign(docid, pid):
	assign = patient.query.get_or_404([docid, pid])
	db.session.delete(assign)
	db.session.commit()
	flash('The apatient assignment has been deleted!', 'success')
	return redirect(url_for('home'))
