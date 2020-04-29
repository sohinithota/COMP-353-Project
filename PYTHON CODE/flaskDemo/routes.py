import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateDoctorAccountForm, UpdatePatientAdministratorAccountForm, PostForm, AssignForm, AssignUpdateForm, CheckInForm
from flaskDemo.models import Accounts, Bed, Doctor, MedicalDevices, Patient, PatientAdministrator
from flaskDemo.models import getDoctor, getPatientAdministrator
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from sqlalchemy.exc import IntegrityError


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		try:
			user = Accounts.query.filter_by(accountName=form.accountname.data).first()
			if user and bcrypt.check_password_hash(user.accountPassword, form.password.data):
				login_user(user)
				next_page = request.args.get('next')
				return redirect(next_page) if next_page else redirect(url_for('home'))
			else:
				flash('Login Unsuccessful. Please check account name and password', 'danger')
		except ValueError:
			flash('Login Unsuccessful. Please check account name and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/home")
@login_required
def home():
	data = []
	if current_user.accountType == 1:
		currentPatientAdmin = db.session.query(PatientAdministrator).filter(PatientAdministrator.accountID == current_user.id).first()
		assignedPatients = db.session.query(Patient).filter(Patient.patientadministratorID == currentPatientAdmin.id).all()
		for x in assignedPatients:
			if (x.departTime is None):
				if (x.minit is None) or (x.minit == ""):
					name = x.fname + " " + x.lname
				else:
					name = x.fname + " " + x.minit + " " + x.lname
				data.append({"name":name, "id":x.id, "ssn":x.ssn, "arrivalTime":x.arrivalTime, "address":x.address, "medicalCondition":x.medicalCondition, "inBed":x.inBed, "bedID":x.bedID, "doctorID":x.doctorID})
			else:
				pass
	else:
		currentDoctor = db.session.query(Doctor).filter(Doctor.accountID == current_user.id).first()
		assignedPatients = db.session.query(Patient).filter(Patient.doctorID == currentDoctor.id).all()
		for x in assignedPatients:
			if (x.departTime is None):
				if (x.minit is None) or (x.minit == ""):
					name = x.fname + " " + x.lname
				else:
					name = x.fname + " " + x.minit + " " + x.lname
				data.append({"name":name, "id":x.id, "ssn":x.ssn, "arrivalTime":x.arrivalTime, "sex":x.sex, "medicalCondition":x.medicalCondition, "inBed":x.inBed, "bedID":x.bedID, "patientadministratorID":x.doctorID})
			else:
				pass
	return render_template('assign_home.html', patientInformation = data)
	
	# results = Patient.query.all()
	# return render_template('assign_home.html', outString = results)
	# results1 = doctor.query.all()
	# return render_template('assign_home.html', outString1 = results1)
	posts = Post.query.all()
	return render_template('home.html', posts=posts)
	results3 = assignment.query.all()
	results2 = Patient.query.join(assignment,Patient.patientID == assignment.patientID).add_columns(Patient.fname, Patient.lname, Patient.ssn, assignment.adminID).join(doctor, doctor.docID == assignment.docID).add_columns(doctor.docfname,doctor.doclname)
	results = Patient.query.join(assignment,Patient.patientID == assignment.patientID).add_columns(Patient.fname, Patient.lname, Patient.ssn, assignment.adminID)
	return render_template('home.html', title='Join', joined_1_n = results, joined_m_n = results2, currentUser = current_user)

@app.route("/about")
def about():
	return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		try:
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			user = Accounts(accountName = form.accountname.data, accountPassword = hashed_password, accountType = form.accounttype.data)
			db.session.add(user)
			db.session.commit()
			flash('An account has been created! You are now able to log in to it.', 'success')
			return redirect(url_for('register'))
		except IntegrityError:
			flash('Invalid account information. Try again.')
			return redirect(url_for('register'))
	return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('login'))

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
	if current_user.accountType == 0:
		form = UpdateDoctorAccountForm()
	else:
		form = UpdatePatientAdministratorAccountForm()
	
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		current_user.accountName = form.accountname.data
		current_user.accountPassword = hashed_password
		
		accountID = current_user.id
		if current_user.accountType == 0:
			test = db.session.query(Doctor).filter(Doctor.id == form.associatewithemployee.data)
			test2 = db.session.query(Doctor).filter(Doctor.accountID == accountID)
			test2.update({Doctor.accountID:None})
			test.update({Doctor.accountID:accountID})
		else:
			test = db.session.query(PatientAdministrator).filter(PatientAdministrator.id == form.associatewithemployee.data)
			test2 = db.session.query(PatientAdministrator).filter(PatientAdministrato.accountID == accountID)
			test2.update({PatientAdministrator.accountID:None})
			test.update({PatientAdministrator.accountID:accountID})
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('home'))
	elif request.method == 'GET':
		form.accountname.data = current_user.accountName
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title = 'Account', image_file = image_file, form = form)

@app.route("/checkin", methods = ['GET', 'POST'])
@login_required
def checkin():
	if current_user.accountType != 1:
		return redirect(url_for('home'))
	
	form = CheckInForm()
	print("FUCK")
	if form.validate_on_submit():
		patient = Patient(fname=form.firstName.data, minit=form.middleInit.data, lname=form.lastName.data, ssn=form.ssn.data, bdate=form.birthdate.data, address=form.address.data, sex=form.sex.data, arrivalTime=datetime.now(), departTime = None, medicalCondition = form.medicalCondition.data, patientadministratorID = db.session.query(PatientAdministrator).filter(PatientAdministrator.accountID == current_user.id).first().id)
		db.session.add(patient)
		db.session.commit()
		return redirect(url_for('home'))
	return render_template('checkin.html', title = 'Check In Patient', form = form)

@app.route("/assign/new", methods=['GET', 'POST'])
@login_required
def new_assign():
	form = AssignForm()
	if form.validate_on_submit():
		assign = Patient(patfname=form.patfname.data, patlname=form.patlname.data, pid=form.pid.data)
		assign1 = doctor(docid=form.docid.data)
		assign2 = assignment(docid=form.docid.data, pid=form.pid.data)
		db.session.add(assign)
		db.session.add(assign1)
		db.session.add(assign2)
		db.session.commit()
		flash('You have added a new Patient!', 'success')
		return redirect(url_for('home'))
	return render_template('create_assign.html', title='New Assignment',
						   form=form, legend='New Assignment')

@app.route("/assign/<docid>/<pid>")
@login_required
def assign(docid, pid):
   assign = Patient.query.get_or_404([docid,pid])
   return render_template('assign.html', title=str(assign.pid) + "_" + str(assign1.docid), assign=assign, now=datetime.utcnow())

@app.route("/assign/<docid>/<pid>update", methods=['GET', 'POST'])
@login_required
def update_assign(docid, pid):
	assign = Patient.query.get_or_404([docid, pid])
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
	assign = Patient.query.get_or_404([docid, pid])
	db.session.delete(assign)
	db.session.commit()
	flash('The apatient assignment has been deleted!', 'success')
	return redirect(url_for('home'))
