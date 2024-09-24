from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import date

db = SQLAlchemy(app)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # 'admin', 'customer', 'service_professional'
   
users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    #change id to role id r_id to identify influencers, sponsors
    id = db.Column(db.Integer, primary_key=True)
    
    username = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(120), nullable=False)
    #confirm_password = db.Column(db.String(120), nullable=False)
    
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_flagged = db.Column(db.Boolean, nullable=False, default=False)
    
   
    roles= db.relationship('Role', backref='user', lazy=True)
   
notifications = db.relationship('Notification', backref='user', lazy=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reciever_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)

class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email  = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    contact = db.Column(db.String(80), nullable=False)
    service_type = db.Column(db.String(80), nullable=False)
    #expertise = db.Column(db.String(80), nullable=False)
    experience = db.Column(db.String(80), nullable=True)
    
    is_verified = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)
    is_suspended = db.Column(db.Boolean, default=False)
    
    users = db.relationship('User', backref='professional', lazy=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    name = db.Column(db.String(80), nullable=False)
    email  = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    contact = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    #date= db.Column(db.date, nullable=False)
    users = db.relationship('User', backref='customer', lazy=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #admin_level = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='admin', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    type = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(80), nullable=False)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    
    
    is_accepted = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_canceled = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)

service_requests = db.relationship('Service', backref='request', lazy=True)
    
    

def add_roles():
    list = ['Admin', 'Professional', 'Customer']
    for role_name in list:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    db.session.commit()
    print("Roles added successfully.")
    
with app.app_context():
    db.create_all()
    add_roles()
    

    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        admin_role_id = admin_role.id
        if not User.query.filter_by(role_id=admin_role_id).first():
     
            password_hash = generate_password_hash('admin')
            admin = User(username='admin', passhash=password_hash, role_id=admin_role_id, is_admin=True, is_flagged=False)
            db.session.add(admin)
            db.session.commit()