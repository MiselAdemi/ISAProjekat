from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField
from models import db, User, Restaurant

class SignupForm(Form):
	first_name = TextField("Ime",  [validators.Required("Please enter your first name.")])
	last_name = TextField("Prezime",  [validators.Required("Please enter your last name.")])
	email = TextField("Email adresa",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
	password = PasswordField('Sifra', [validators.Required("Please enter a password.")])
	submit = SubmitField("Ristrujte se")
 
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
 
	def validate(self):
		if not Form.validate(self):
			return False
     
		user = User.query.filter_by(email = self.email.data.lower()).first()
		if user:
			self.email.errors.append("Ova email adresa je vec zauzeta.")
			return False
		else:
			return True


class SigninForm(Form):
	email = TextField("Email adresa",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
	password = PasswordField('Sifra', [validators.Required("Please enter a password.")])
	submit = SubmitField("Uloguj se")
   
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
 
	def validate(self):
		if not Form.validate(self):
			return False
     
		user = User.query.filter_by(email = self.email.data.lower(), active = 1).first()
		if user and user.check_password(self.password.data):
			return True
		elif not user:
			self.email.errors.append("Nalog nije aktiviran.")
			return False
		else:
			self.email.errors.append("Pogresna email adresa ili sifra")
			return False



class AddRestaurante(Form):
	name = TextField("Naziv restorana",  [validators.Required("Niste uneli naziv.")])
	type = TextField('Tip restorana', [validators.Required("Niste uneli tip restorana.")])
	submit = SubmitField("Dodaj restoran")
   
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
 
	def validate(self):
		if not Form.validate(self):
			return False
     
		restaurante = Restaurant.query.filter_by(name = self.name.data.lower()).first()
		if restaurante:
			self.name.errors.append("Restoran sa ovim imenom vec postoji.")
			return False
		else:
			return True


class EditRestaurant(Form):
	name = TextField("Naziv",  [validators.Required("Niste uneli naziv.")])
	type = TextField('Tip restorana', [validators.Required("Niste uneli tip restorana.")])
	submit = SubmitField("Sacuvaj izmene")
   
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
 
	def validate(self):
		if not Form.validate(self):
			return False