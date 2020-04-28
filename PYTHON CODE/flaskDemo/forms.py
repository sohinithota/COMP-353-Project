from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import User, patient, getpatient, getpatientFactory, doctor, getdoctor, getdoctorFactory, assignment, getassignment, getassignmentFactory
from wtforms.fields.html5 import DateField

pid = patient.query.with_entities(patient.patientID)
docid = doctor.query.with_entities(doctor.docID)

#  or could have used ssns = db.session.query(Department.mgr_ssn).distinct()
# for that way, we would have imported db from flaskDemo, see above

results=list()
for row in pid:
    rowDict=row._asdict()
    results.append(rowDict)
patientChoices = [(row['patientID'],row['patientID']) for row in results]
regex1='^((((19|20)(([02468][048])|([13579][26]))-02-29))|((20[0-9][0-9])|(19[0-9][0-9]))-((((0[1-9])'
regex2='|(1[0-2]))-((0[1-9])|(1\d)|(2[0-8])))|((((0[13578])|(1[02]))-31)|(((0[1,3-9])|(1[0-2]))-(29|30)))))$'
regex=regex1 + regex2

result2=list()
for row in docid:
    rowDict=row._asdict()
    result2.append(rowDict)
doctorChoices = [(row['docID'],row['docID']) for row in result2]  # change

class RegistrationForm(FlaskForm):
    accountname = StringField('Account Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
			
class LoginForm(FlaskForm):
    accountname = StringField('Account Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

    
class AssignUpdateForm(FlaskForm):

#    dnumber=IntegerField('Department Number', validators=[DataRequired()])
    adminid = HiddenField("")
    
    patfname = StringField('Patient\'s First Name:', validators=[DataRequired(),Length(max=15)])
#  Commented out using a text field, validated with a Regexp.  That also works, but a hassle to enter ssn.
#    mgr_ssn = StringField("Manager's SSN", validators=[DataRequired(),Regexp('^(?!000|666)[0-8][0-9]{2}(?!00)[0-9]{2}(?!0000)[0-9]{4}$', message="Please enter 9 digits for a social security.")])

    patlname = StringField('Patient\'s Last Name:', validators=[DataRequired(),Length(max=15)])
#  Commented out using a text field, validated with a Regexp.  That also works, but a hassle to enter ssn.
#    mgr_ssn = StringField("Manager's SSN", validators=[DataRequired(),Regexp('^(?!000|666)[0-8][0-9]{2}(?!00)[0-9]{2}(?!0000)[0-9]{4}$', message="Please enter 9 digits for a social security.")])


#  One of many ways to use SelectField or QuerySelectField.  Lots of issues using those fields!!
    pid = SelectField('Patient ID:',choices=patientChoices, coerce = int)  # empChoices defined at top
    
    medcondition = StringField('Patient\'s Medical Condition:')
    
# Doctor ID
    docid = SelectField("Doctor ID", choices=doctorChoices, coerce = int)    
     
    
# the regexp works, and even gives an error message
#    mgr_start=DateField("Manager's Start Date:  yyyy-mm-dd",validators=[Regexp(regex)])
#    mgr_start = DateField("Manager's Start Date")

#    mgr_start=DateField("Manager's Start Date", format='%Y-%m-%d')
    #hours = DateField('Hours', validators=[DataRequired(),Length(max=30)]) #hours field in works_on  # This is using the html5 date picker (imported)
    submit = SubmitField('Update this Assignment')

# got rid of def validate_dnumber
    
    def validate_doc(self, doclname):    # apparently in the company DB, dname is specified as unique
         assign1 = doctor.query.filter_by(doclname=doclname.data).first()
         if assign1 and (str(doctor.docID) != str(self.docID.data)):
             raise ValidationError('That doctor is already attending someone. Please choose a different doctor.')
                  
         #if assign:
             #raise ValidationError('That doctor is already attending someone. Please choose a different doctor.')

class AssignForm(AssignUpdateForm):

    pid = IntegerField("Patient ID", validators=[DataRequired()])
    submit = SubmitField('Add this Patient')

    def validate_pid(self, pid):    #because dnumber is primary key and should be unique
        assign = patient.query.filter_by(pid=pid.data).first()
        if assign:
            raise ValidationError('That patient has already been assigned. Please choose a different one.')

