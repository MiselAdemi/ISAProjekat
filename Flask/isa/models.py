from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
 
db = SQLAlchemy()

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	first_name = db.Column(db.String(30))
	last_name = db.Column(db.String(30))
	email = db.Column(db.String(255), unique=True)
	password = db.Column(db.String(200))
	role = db.Column(db.String(10))
	active = db.Column(db.Integer)
   
	def __init__(self, first_name, last_name, email, password, role, active):
		self.first_name = first_name.title()
		self.last_name = last_name.title()
		self.email = email.lower()
		self.set_password(password)
		self.role = role
		self.active = 0
     
	def set_password(self, password):
		self.password = generate_password_hash(password)
   
	def check_password(self, password):
		return check_password_hash(self.password, password)


class friend_request(db.Model):
	__tablename__ = 'friend_request'
	from_id = db.Column(db.Integer, primary_key = True)
	to_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True)

	def __init__(self, from_id, to_id):
		self.from_id = from_id
		self.to_id = to_id


class Friends(db.Model):
	__tablename__ = 'friends'
	user_one = db.Column(db.Integer, primary_key = True)
	user_two = db.Column(db.Integer, primary_key = True)

	def __init__(self, user_one, user_two):
		self.user_one = user_one
		self.user_two = user_two


class Restaurant(db.Model):
	__tablename__ = 'restaurant'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(255))
	type = db.Column(db.String(255))
	menu = db.Column(db.String(50))

	def __init__(self, name, type, menu):
		self.name = name
		self.type = type
		self.menu = menu.lower()

class RestaurantManager(db.Model):
	__tablename__ = 'restaurant_manager'
	id = db.Column(db.Integer, primary_key = True)
	manager = db.Column(db.Integer)
	restaurant = db.Column(db.Integer)

	def __init__(self, manager, restaurant):
		self.manager = manager
		self.restaurant = restaurant