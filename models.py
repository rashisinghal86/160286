from extensions import db
# from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_security import UserMixin, RoleMixin
import uuid


roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)


    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime(), default=datetime.utcnow)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))  # Add fs_uniquifier field
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

     # Add the login tracking fields
    current_login_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    current_login_ip = db.Column(db.String(45))
    last_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer, default=0)
    
class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email  = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    filename = db.Column(db.String(80), unique=True, nullable=False)
    contact = db.Column(db.String(80), nullable=False)
    service_type = db.Column(db.String(80), nullable=False)
    experience = db.Column(db.String(80), nullable=True)
    location = db.Column(db.String(80), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email  = db.Column(db.String(80), nullable=False)
    contact = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='admin', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    services = db.relationship("Service", backref="category", lazy=True, cascade="all, delete-orphan")

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    name = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    price = db.Column(db.String(64), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    schedules = db.relationship('Schedule', backref='service', lazy=True, cascade="all, delete-orphan")
    bookings = db.relationship('Booking', backref='service', lazy=True, cascade="all, delete-orphan")

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    schedule_datetime = db.Column(db.DateTime, nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)
    is_pending = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    is_cancelled = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(80), nullable=False)
    bookings = db.relationship('Booking', backref='transaction', lazy=True, cascade="all, delete-orphan")

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    date_of_completion = db.Column(db.Date, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    remarks = db.Column(db.String(1024), nullable=True)


def add_roles():
    roles = ['Admin', 'Professional', 'Customer']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    db.session.commit()
    print("Roles added successfully.")

def create_default_admin():
    admin_role = Role.query.filter_by(name='Admin').first()
    if admin_role:
        if not User.query.filter_by(email='admin@example.com').first():
            password_hash = generate_password_hash('admin123!@#')
            admin = User(
                email='admin@example.com',
                username='admin',
                password=password_hash,
                active=True,
                confirmed_at=datetime.utcnow(),
                role_id=admin_role.id, #
                roles=[admin_role]
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
            

# Ensure the database is initialized and roles/admin are added
# with app.app_context():
#     db.create_all()
#     add_roles()
#     create_default_admin()