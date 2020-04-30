from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from random import randint
import os.path

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# Change cfn:naiman to your_username:your_password
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cfn:naiman@localhost/healthcareprovider'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskDemo import routes
from flaskDemo import models 

models.db.create_all()

if os.path.isfile("log.txt"):
	pass
else:
	with open("log.txt", "w") as f:
		f.write("Randomly assigning Patient Administrators to Patients...")

		paID = []
		pID = []

		for x in models.getPatientAdministrator():
			paID.append(x.id)

		for x in models.getPatient():
			pID.append(x.id)

		max = db.session.query(models.PatientAdministrator).count()
		for x in pID:
			if max == 0:
				assignedPAID = paID[0]
			else:
				assignedPAID = paID[randint(0,max - 1)]
			test = db.session.query(models.Patient).filter(models.Patient.id == x)
			test.update({models.Patient.patientadministratorID:assignedPAID})
		db.session.commit()
		f.write("Task complete")
		f.close()