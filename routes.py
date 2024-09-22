from app import app
from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Role, Professional, Customer, Notification
from functools import wraps


 
@app.route('/')
def home():
    return (render_template('home.html'))
    
    #register routes
@app.route('/register')
def register():
    role=Role.query.all()
    return render_template('register.html', role=role)



@app.route('/login')
def login_user():
    return render_template('login_user.html')
#prof pages
@app.route('/login_prof')
def login_prof():
    return render_template('professional/login_prof.html')
#accept or reject appointments
@app.route('/accept_appointments')
def accept_appointments():
    return render_template('professional/accept_appointments.html')
#view appointments
@app.route('/view_appointments_prof')
def view_appointments_prof():
    return render_template('professional/view_appointments_prof.html')
#view profile
@app.route('/view')
def view():
    return render_template('appointment/view.html')

@app.route('/accept')
def accept():
    return render_template('appointment/accept.html')

@app.route('/reject')
def reject():
    return render_template('appointment/reject.html')




@app.route('/login_cust')
def login_cust():
    return render_template('customer/login_cust.html')


@app.route('/login_admin')
def login_admin():
    return render_template('admin_db.html')


@app.route('/signout')
def signout():
    return render_template('signout.html')
@app.route('/view_prof')
def view_prof():
    return render_template('prof.html')
@app.route('/add_prof')
def add_prof():
    return render_template('professional/add_prof.html')

@app.route('/flag_prof')
def flag_prof():
    return render_template('professional/flag_prof.html')



@app.route('/view_services')
def view_services():
    return render_template('services/services.html')

@app.route('/add_services')
def add_services():
    return render_template('services/add_services.html')

@app.route('/edit_services')
def edit_services():
    return render_template('services/edit_services.html')

@app.route('/delete_services')
def delete_services():
    return render_template('services/delete_services.html')


@app.route('/view_user2')
def view_cust():
    return render_template('cust.html')

@app.route('/view_appointments')
def view_appointments():
    return render_template('appointments.html')

if __name__ == '__main__':
    app.run(debug=True)
    