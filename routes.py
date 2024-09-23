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

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    role_id = request.form.get('role_id')
    
    
    if not username or not password or not confirm_password:
        flash('Please fill out the fields')
        return redirect(url_for('register'))

    if password != confirm_password:
        flash('Passwords do not match')
        return redirect(url_for('register')) 
    
    user = User.query.filter_by(username=username).first()

    if user:
        flash('Username already exists')
        return redirect(url_for('register'))
    
    password_hash = generate_password_hash(password)

    new_user = User(username=username, passhash=password_hash, role_id=role_id)

    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))



     # login routes
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    return 'username: {}, password: {}'.format(username, password)

    

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


#@app.route('/login_admin')
#def login_admin():
 #   return render_template('login_admin.html')


@app.route('/signout')
#@auth_reqd
def signout():
    session.pop('user_id')
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
    