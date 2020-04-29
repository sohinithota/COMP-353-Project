# Creates classes that access the DB

from datetime import datetime
from flaskDemo import db, login_manager
from flask_login import UserMixin
from functools import partial
from sqlalchemy import orm

db.Model.metadata.reflect(db.engine)

class Accounts(db.Model, UserMixin):
	__table__ = db.Model.metadata.tables['accounts']

class Bed(db.Model):
	__table__ = db.Model.metadata.tables['bed']

class Doctor(db.Model):
	__table__ = db.Model.metadata.tables['doctor']
	
class MedicalDevices(db.Model):
	__table__ = db.Model.metadata.tables['medicaldevices']
	
class Patient(db.Model):
	__table__ = db.Model.metadata.tables['patient']
	
class PatientAdministrator(db.Model):
	__table__ = db.Model.metadata.tables['patientadministrator']
	
# class Post(db.Model):
	 # __table_args__ = {'extend_existing': True}
	 # id = db.Column(db.Integer, primary_key=True)
	 # title = db.Column(db.String(100), nullable=False)
	 # date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	 # content = db.Column(db.Text, nullable=False)
	 # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	 # def __repr__(self):
		 # return f"Post('{self.title}', '{self.date_posted}')"
		 
@login_manager.user_loader
def load_user(user_id):
	return Accounts.query.get(int(user_id))

def getPatientAdministrator(columns=None):
	u = PatientAdministrator.query
	if columns:
		u = u.options(orm.load_only(*columns))
	return u
	
def getPatientAdministratorFactory(columns=None):
	return partial(getPatientAdministrator, columns=columns)	  
	
def getPatient(columns=None):
	u = Patient.query
	if columns:
		u = u.options(orm.load_only(*columns))
	return u
	
def getPatientFactory(columns=None):
	return partial(getPatient, columns=columns)
		
def getDoctor(columns=None):
	u = Doctor.query
	if columns:
		u = u.options(orm.load_only(*columns))
	return u
	
def getDoctorFactory(columns=None):
	return partial(getDoctor, columns=columns)	  
	
# class assignment(db.Model):
	# __table__ = db.Model.metadata.tables['assignment']
	
# def getassignment(columns=None):
	# u = assignment.query
	# if columns:
		# u = u.options(orm.load_only(*columns))
	# return u

# def getassignmentFactory(columns=None):
	# return partial(getassignment, columns=columns)	  
	
	

  
