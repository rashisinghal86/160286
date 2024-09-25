from app import app
from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Role, Professional, Customer, Notification
from functools import wraps
#----- home page-----
@app.route('/')
def home():
    # if user_id is in session, then render the home page
    if 'user_id' in session:
        return render_template('home.html')
    else:
        flash('Please login to access the page')
        return redirect(url_for('login'))
#-------decorator for authentication----------------    
#decorator for auth_required
def auth_reqd(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
                                           return func(*args, **kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
    return inner

#--1. registering a user-----------------------------------
@app.route('/register')
def register():
    role = Role.query.all()
    print(role)
    return render_template('register.html', role=role)

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    role_id = int(request.form['role_id'])
    
    
    if not username or not password or not confirm_password:
        flash('Please enter all the fields')
        return redirect(url_for('register'))
    
    if password != confirm_password:
        flash('Passwords do not match')
        return redirect(url_for('register'))
    
    user = User.query.filter_by(username=username).first()
    if user:
        flash ('Username already exists')
        return redirect(url_for('register'))
    
    
      
    password_hash = generate_password_hash(password)
    
    new_user= User(username=username, passhash=password_hash,  role_id=role_id)

    db.session.add(new_user)
    db.session.commit()

    flash('User registered successfully')
    return redirect(url_for('login'))
#---2. login of all users and redirection to respective/ profile update or dashboard-----------------------------------

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']


    if not username or not password:
        flash("please enter all the fields")
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Username has been taken')
        return redirect(url_for('login'))
    
    
    if not check_password_hash(user.passhash, password):
        flash('Incorrect password')
        return redirect(url_for('login'))
    
    session['user_id']= user.id
    flash('you have logged in successfully')
    #check role of user and redirect to respective page
    role = Role.query.get (user.role_id)
    #check code at admin.txt
    if role.name =='Admin':
        return render_template('admin_db.html')
    #if role.name == 'admin':
     #   existing_admin = User.query.filter_by(role_id=role.id).first()
      #  if existing_admin:
       #     flash('An admin user already exists. Cannot create another admin.')
        #    #return redirect(url_for('user_creation_form'))
         #   return render_template('admin_db.html')
    

    elif role.name == 'Professional':
        professional = Professional.query.filter_by(user_id=user.id).first()
        if professional:
            #return ('already registered professional page')
            return redirect(url_for('prof_db', username=professional.users.username))
        else:
            return redirect(url_for('register_pdb'))
        
    elif role.name == 'Customer':
        customer = Customer.query.filter_by(user_id=user.id).first()
        if customer:
            #return ('already registered customer page')
            return redirect(url_for('cust_db', username=customer.users.username))
        else:
            return redirect(url_for('register_cdb'))
    else:
        return redirect(url_for('login'))
    
#---2a proffessional registration-----------------------------------
@app.route('/register_pdb')
def register_pdb():
    return render_template('register_pdb.html')

@app.route('/register_pdb', methods=['POST'])
def register_pdb_post():
    
    user = User.query.get(session['user_id'])
    professional= Professional.query.filter_by(user_id=user.id).first()
    if professional:
        #return ('already registered professional page' )
        return redirect(url_for('prof_db', name=professional.users.name))
    
    email = request.form['email']
    name = request.form['name']
    username = request.form['username']
    contact = request.form['contact']
    service_type = request.form['service_type']
    experience = request.form['experience']
    
    
    password    = request.form['password']
    
    if not email or not name or not username or not contact or not service_type or not experience or not password:
        flash('Please enter all the fields')
    
        return redirect(url_for('register_pdb'))
    
    new_professional = Professional(user_id=user.id, email=email, name=name, username=username, contact=contact, service_type=service_type, experience=experience)
    db.session.add(new_professional)
    db.session.commit()
    
    #Check if professional-specific details are already provided\    
    flash('professional registered successfully')
    return redirect(url_for('prof_db'))

#---2b customer registration-----------------------------------

@app.route('/register_cdb')
def register_cdb():
    return render_template('register_cdb.html')


@app.route('/register_cdb', methods=['POST'])
def register_cdb_post():
    
    user = User.query.get(session['user_id'])
    customer = Customer.query.filter_by(user_id=user.id).first()
    if customer:
        #return ('already registered customer page' )
        return redirect(url_for('cust_db', name=customer.users.name))
    
    email = request.form['email']
    name = request.form['name']
    username = request.form['username']
    contact = request.form['contact']
    location = request.form['location']
    password = request.form['password']
    
    if not email or not name or not username or not contact or not location or not password:
        flash('Please enter all the fields')
        return redirect(url_for('register_cdb'))
    
    new_customer = Customer(user_id=user.id, email=email, name=name, username=username, contact=contact, location=location)
    db.session.add(new_customer)
    db.session.commit()
    
    #Check if customer-specific details are already provided\    
    flash('Customer registered successfully')
    return redirect(url_for('cust_db'))


@app.route('/prof_db')
def prof_db():
    return render_template('prof_db.html')

@app.route('/cust_db')
def cust_db():
    return render_template('cust_db.html')

#-----3. signout-------------------------
@app.route('/signout')
@auth_reqd
def signout():
    session.pop('user_id')
    return render_template('home.html')

@app.route('/profile')
@auth_reqd
def profile():
    user = User.query.get(session['user_id'])
    role = Role.query.get (user.role_id)
    #if user is admin, redirect to profile_admin page
    if role.name == 'Admin':
        return render_template('profile_admin.html', user=user)
    elif role.name == 'Professional':
        professional = Professional.query.filter_by(user_id=user.id).first()
        return render_template('profile_prof.html', user=user, professional=professional)
    elif role.name == 'Customer':
        customer = Customer.query.filter_by(user_id=user.id).first()
        return render_template('profile_cust.html', user=user, customer=customer)
    return render_template('profile.html', user=user)
   
@app.route('/profile', methods=['POST'])
@auth_reqd
def profile_post():
    username=request.form.get('username')
    cpassword=request.form.get('cpassword')
    password=request.form.get('password')
    name=request.form.get('name')

    if not username or not cpassword or not password:
        flash('Please fill out the fields')
        return redirect(url_for('profile'))
    
    #check if current password entered to update is correct
    user = User.query.get(session['user_id'])
    if not check_password_hash(user.passhash, cpassword):
        flash('Incorrect current password')
        return redirect(url_for('profile'))
    #check if new username id available
    if username != user.username:
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('profile'))
        
    new_password_hash = generate_password_hash(password)
    user.username = username
    user.passhash = new_password_hash
    user.name = name

    db.session.commit()
    flash('Profile updated successfully')
    return redirect(url_for('profile'))
    

    
    
    