from flask import Flask
 
app = Flask(__name__)
 
app.secret_key = 'development key'
 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'contact@example.com'
app.config["MAIL_PASSWORD"] = 'your-password'
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/ISA'
 
from models import db
db.init_app(app)
 
import isa.routes