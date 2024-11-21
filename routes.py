from app import app
from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Role,Admin, Professional, Customer, Category, Service, Schedule, Transaction, Booking
from datetime import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/uploads'

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
#-------decorator for authentication----------------    
#decorator for auth_required
def auth_reqd(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' in session:
            return func(*args,**kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
            
    return inner

def admin_reqd(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        role = Role.query.get(user.role_id)
        if role.name != 'Admin':
            flash('You are not authorized to access this page')
            return redirect(url_for('home'))
        return func(*args,**kwargs)
    return inner

def blocked_check(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        role = Role.query.get(user.role_id)
        if role.name == 'Professional':
            professional = Professional.query.filter_by(user_id=user.id).first()
            if professional.is_flagged:
                return render_template('flag_prof.html', professional=professional)
        elif role.name == 'Customer':
            customer = Customer.query.filter_by(user_id=user.id).first()
            if customer.is_blocked:
                return render_template('block_cust.html', customer=customer)
        return func(*args,**kwargs)
    return inner

#----- home page-----
@app.route('/')
@auth_reqd
def home():
    user = User.query.get(session['user_id'])
    session['user_id']= user.id
    #check role of user and redirect to respective page
    role = Role.query.get (user.role_id)
    #check code at admin.txt
    if role.name =='Admin':
        admin = Admin.query.filter_by(user_id=user.id).first()
        if admin:
            return redirect(url_for('admin_db', username=admin.user.username))
        
    elif role.name == 'Professional':
        professional = Professional.query.filter_by(user_id=user.id).first()
        if professional:
            return redirect(url_for('prof_db', username=professional.users.username))
    elif role.name == 'Customer':
        customer = Customer.query.filter_by(user_id=user.id).first()
        if customer:
            return redirect(url_for('cust_db', username=customer.users.username))
    return render_template('home.html', user=user)
    
   


#--1. registering a user-----------------------------------
@app.route('/register')
def register():
    role = Role.query.all()
    
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
        flash('You are not registered, Register ^ to login')
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
        admin = Admin.query.filter_by(user_id=user.id).first()
        if admin:
            
            return redirect(url_for('admin_db', username=admin.user.username))
            
        else:
            return redirect(url_for('register_adb'))
 
    elif role.name == 'Professional':
        professional = Professional.query.filter_by(user_id=user.id).first()
        print(professional)
        print(professional)
        print(professional)


        if not professional:
            return redirect(url_for('register_pdb'))
        if professional.is_flagged:
                professional = Professional.query.filter_by(user_id=user.id).first()
                return render_template('flag_prof.html', professional=professional)

        if professional and professional.is_verified:
            print(professional,'hi')
            
            #return ('already registered professional page')
            return redirect(url_for('prof_db', username=professional.users.username))
        if professional and not professional.is_verified:
            professional = Professional.query.filter_by(user_id=user.id).first()
            return render_template('verify_prof.html',professional=professional)
            
        
        
    elif role.name == 'Customer':
        customer = Customer.query.filter_by(user_id=user.id).first()
        if customer.is_blocked:
            return render_template('block_cust.html', customer=customer)
        if customer:
            #return ('already registered customer page')
            return redirect(url_for('cust_db', username=customer.users.username))
        else:
            return redirect(url_for('register_cdb'))
    else:
        #return redirect(url_for('home'))
        return redirect(url_for('login'))
    
#---2a admin registration-----------------------------------
@app.route('/register_adb')
def register_adb():
    return render_template('register_adb.html')

@app.route('/register_adb', methods=['POST'])
def register_adb_post():
    
    user = User.query.get(session['user_id'])
    admin = Admin.query.filter_by(user_id=user.id).first()
    if admin:
        #return ('already registered admin page' )
        return redirect(url_for('admin_db', username=admin.user.username))
        #return redirect(url_for('admin_db', name=admin.user.name))
    name = request.form['name']
    
    
    if not name:
        flash('Please enter all the fields')
        return redirect(url_for('register_adb'))
    
    new_admin = Admin(user_id=user.id, name=name)
    db.session.add(new_admin)
    db.session.commit()
    
    #Check if admin-specific details are already provided\    
    flash('Admin registered successfully')
    return redirect(url_for('admin_db'))
    
#---2a proffessional registration-----------------------------------
@app.route('/register_pdb')
def register_pdb():
    return render_template('register_pdb.html')

@app.route('/register_pdb', methods=['POST'])
def register_pdb_post():
    
    # professional= Professional.query.filter_by(user_id=user.id).first()

    # if professional:
    #     #return ('already registered professional page' )
    #     return redirect(url_for('prof_db', name=professional.users.username))
    
    email = request.form['email']
    name = request.form['name']
    #username = request.form['username']
    contact = request.form['contact']
    service_type = request.form['service_type']
    experience = request.form['experience']
    location = request.form['location']
    
    #file upload 
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully!')

   #password    = request.form['password']
    if not email or not name or not contact or not service_type or not experience:
        flash('Please enter all the fields')
        return redirect(url_for('register_pdb'))

    user = User.query.get(session['user_id'])
  
    new_professional = Professional(user_id=user.id, email=email, name=name, contact=contact, service_type=service_type, experience=experience, location=location, filename=filename)   
    db.session.add(new_professional)
    db.session.commit()

    
    #Check if professional-specific details are already provided  
    flash('professional registered successfully')
    # return redirect(url_for('prof_db'))
    professional = Professional.query.filter_by(user_id=user.id).first()
    print(professional)
    print(professional)
    print(professional)


    if not professional:
        return redirect(url_for('register_pdb'))
    if professional.is_flagged:
            professional = Professional.query.filter_by(user_id=user.id).first()
            return render_template('flag_prof.html', professional=professional)

    if professional and professional.is_verified:
        print(professional,'hi')
        
        #return ('already registered professional page')
        return redirect(url_for('prof_db', username=professional.users.username))
    if professional and not professional.is_verified:
        professional = Professional.query.filter_by(user_id=user.id).first()
        return render_template('verify_prof.html',professional=professional)
        


@app.route('/admin/professionals')
@admin_reqd
def professionals():   
    professionals=Professional.query.all()
    pname = request.args.get('pname') or ''
    pservice_type = request.args.get('pservice_type') or ''
    plocation = request.args.get('plocation') or ''
    print(pname, pservice_type, plocation)

    if pname:
        professionals = Professional.query.filter(Professional.name.ilike(f'%{pname}%')).all()
    return render_template('professionals.html', professionals=professionals, pname=pname, pservice_type=pservice_type, plocation=plocation)


@app.route('/admin/pending_professionals')
@admin_reqd
def pending_professionals():
    pending_professionals = Professional.query.filter_by(is_verified=False,is_flagged=False).all()
    approved_professionals = Professional.query.filter_by(is_verified=True).all()
    blocked_professionals = Professional.query.filter_by(is_flagged=True).all()

    #search professionals for search on basis of name, service_type, location, experience
    # professionals=Professional.query.all()
    # pname = request.args.get('pname') or ''
    # pservice_type = request.args.get('pservice_type') or ''
    # plocation = request.args.get('plocation') or ''
    # print(pname, pservice_type, plocation)

    # # search_professionals = []

    # if pname:
    #     professionals = Professional.query.filter(Professional.name.ilike(f'%{pname}%')).all()
    # # if pservice_type:
    #     professionals = Professional.query.filter(Professional.service_type.ilike(f'%{pservice_type}%')).all()
    # if plocation:
    #     professionals = Professional.query.filter(Professional.location.ilike(f'%{plocation}%')).all()  
    return render_template('pending_professionals.html', pending_professionals=pending_professionals,approved_professionals=approved_professionals, blocked_professionals=blocked_professionals)
        
    #return render_template('pending_professionals.html', pending_professionals=pending_professionals,approved_professionals=approved_professionals, blocked_professionals=blocked_professionals)

# Admin route to approve professional
@app.route('/admin/approve_professional/<int:id>', methods=['POST'])
@admin_reqd
def approve_professional(id):    
    professional = Professional.query.get(id)
    if professional:
        professional.is_verified = True
        #professional.is_flagged = True
        db.session.commit()
        flash(f'Professional {professional.name} approved successfully')
    return redirect(url_for('pending_professionals'))

# Admin route to block professional
@app.route('/admin/block_professional/<int:id>', methods=['POST'])
@admin_reqd
def block_professional(id):    
    professional = Professional.query.get(id)
    if professional:
        professional.is_flagged = True
       
        professional.is_verified = False
        db.session.commit()
        flash(f'Professional {professional.name} blocked successfully')
    return redirect(url_for('pending_professionals'))

# Admin route to unblock professional
@app.route('/admin/unblock_professional/<int:id>', methods=['POST'])
@admin_reqd
def unblock_professional(id):   
    professional = Professional.query.get(id)
    if professional:
        professional.is_flagged = False
        db.session.commit()
        flash(f'Professional {professional.name} unblocked successfully')
    return redirect(url_for('pending_professionals'))

#  professional dashboard link to show all the appointments- accept/ reject
    




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
    #username = request.form['username']
    contact = request.form['contact']
    location = request.form['location']
    password = request.form['password']
    
    if not email or not name or not contact or not location or not password:
        flash('Please enter all the fields')
        return redirect(url_for('register_cdb'))
    
    new_customer = Customer(user_id=user.id, email=email, name=name, contact=contact, location=location)
    db.session.add(new_customer)
    db.session.commit()
    
    #Check if customer-specific details are already provided\    
    flash('Customer registered successfully')
    return redirect(url_for('cust_db'))

#Admin route to search customers and blocked/unblocked.
@app.route('/admin/customers')
@auth_reqd
def customers():  
    customers=Customer.query.all()
    cname = request.args.get('cname') or ''
    clocation = request.args.get('clocation') or ''
    print(cname, clocation)

    if cname:
        customers = Customer.query.filter(Customer.name.ilike(f'%{cname}%')).all()
    return render_template('customers.html', customers=customers, cname=cname, clocation=clocation)

#admin route to manage customers
@app.route('/admin/manage_customers')
@admin_reqd 
def manage_customers():   
    unblocked_customers = Customer.query.filter_by(is_blocked=False).all()
    blocked_customers = Customer.query.filter_by(is_blocked=True).all()

    return render_template('manage_customers.html',unblocked_customers=unblocked_customers, blocked_customers=blocked_customers)

# Admin route to unblock customer
@app.route('/admin/unblock_customer/<int:id>', methods=['POST'])
@admin_reqd
def unblock_customer(id):
    customer = Customer.query.get(id)
    if customer:
        customer.is_blocked = False
        db.session.commit()
        flash(f'Customer {customer.name} unblocked successfully')
    return redirect(url_for('manage_customers'))  

# Admin route to block customer
@app.route('/admin/block_customer/<int:id>', methods=['POST'])
@admin_reqd
def block_customer(id):   
    customer = Customer.query.get(id)
    if customer:
        customer.is_blocked = True
       
        db.session.commit()
        flash(f'Customer {customer.name} blocked successfully')
    return redirect(url_for('manage_customers'))
# ------------------------------------------------------------------------#  

@app.route('/prof_db')
def prof_db():
    prof_name = request.args.get('username') or ''
    #you can use the username to search for the professional in the database and show request accordingly in html according to their location.
    # check for proff in session, and fetch active request accepted by professional
    # pass it into render tempalate and show in html page.
    # [].
    #open_requests = Schedule.query.filter_by(is_pending=True).all()
    # accepted_requests = Booking.query.filter_by(is_accepted=True).all()
    # print(open_requests)

    return render_template('prof_db.html', prof_name=prof_name)
    

@app.route('/prof_db/<int:id>')
def prof_db_post(id):
    booking = Booking.query.get(id)
    pending_booking = Booking.query.filter_by(is_pending=True).all()

    if not booking:
        flash('Booking does not exist')
        return redirect(url_for('prof_db'))
    
    booking.is_pending = False
    booking.is_accepted = True

    booking.professional_id = Professional.query.filter_by(user_id=session['user_id']).first().id
    


    db.session.commit()
    flash('Booking accepted successfully')
    
    return redirect(url_for('prof_db',booking=booking,pending_booking=pending_booking))


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
    flash('Unexpected role. Please contact support.')
    return redirect(url_for('home')) 

@app.route('/profile', methods=['POST'])
@auth_reqd
def profile_post():
    # if user is admin, redirect to profile_admin page
    user = User.query.get(session['user_id'])
    role = Role.query.get(user.role_id)
    
    if role.name == 'Admin':
        
        admin = Admin.query.filter_by(user_id=user.id).first()
        username=request.form.get('username')
        cpassword=request.form.get('cpassword')
        password=request.form.get('password')
        admin.name=request.form.get('name')

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
        user.name = admin.name

        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('home'))
    
    
    elif role.name == 'Professional':
        
        professional = Professional.query.filter_by(user_id=user.id).first()
        if not professional:
            flash('Professional profile not found')
            return redirect(url_for('profile'))

        username=request.form.get('username')
        cpassword=request.form.get('cpassword')
        password=request.form.get('password')
        professional.email = request.form.get('email') or professional.email
        professional.name = request.form.get('name') or professional.name
        professional.contact = request.form.get('contact') or professional.contact
        professional.location = request.form.get('location') or professional.location
        professional.experience = request.form.get('experience') or professional.experience

        if not username or not cpassword or not password:
            flash('Please fill out the fields')
            return redirect(url_for('profile'))
        
        #check if current password entered to update is correct
        #user = User.query.get(session['user_id'])
        if not check_password_hash(user.passhash, cpassword):
            flash('Incorrect current password')
            return redirect(url_for('profile'))
        #check if new username id available
        if username != user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists')
                return redirect(url_for('profile'))   

        new_password_hash = generate_password_hash(password)
        user.username = username
        user.passhash = new_password_hash
        user.name = professional.name
        professional.email = professional.email
        professional.contact = professional.contact
        professional.location = professional.location
        
        professional.experience = professional.experience


        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('home'))
    
    

    elif role.name == 'Customer':
        
        customer = Customer.query.filter_by(user_id=user.id).first()
        if not customer:
            flash('Customer profile not found')
            return redirect(url_for('profile'))

        username=request.form.get('username')
        cpassword=request.form.get('cpassword')
        password=request.form.get('password')
        customer.email = request.form.get('email') or customer.email
        customer.name = request.form.get('name') or customer.name
        customer.contact = request.form.get('contact') or customer.contact
        customer.location = request.form.get('location') or customer.location

        if not username or not cpassword or not password:
            flash('Please fill out the fields')
            return redirect(url_for('profile'))
        
        #check if current password entered to update is correct
        #user = User.query.get(session['user_id'])
        if not check_password_hash(user.passhash, cpassword):
            flash('Incorrect current password')
            return redirect(url_for('profile'))
        #check if new username id available
        if username != user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists')
                return redirect(url_for('profile'))   

        new_password_hash = generate_password_hash(password)
        user.username = username
        user.passhash = new_password_hash
        user.name = customer.name
        customer.email = customer.email
        customer.contact = customer.contact
        customer.location = customer.location
    

        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('home'))
    
    flash('Unexpected role. Please contact support.')
    return redirect(url_for('home'))






    
#-------admin pages-----------------------------------
@app.route('/admin_db')
@admin_reqd
def admin_db():
    categories=Category.query.all()
    category_names = [category.name for category in categories]
    category_sizes = [len(category.services) for category in categories]
    
    
    pending_professionals = [Professional.query.filter_by(is_verified=False).count()]
    blocked_professionals = [Professional.query.filter_by(is_flagged=True).count()]
    approved_professionals = [Professional.query.filter_by(is_verified=True).count()]

    blocked_customers = [Customer.query.filter_by(is_blocked=True).count()]
    unblocked_customers = [Customer.query.filter_by(is_blocked=False).count()]

    return render_template('admin_db.html', categories=categories, category_names=category_names, category_sizes=category_sizes, blocked_professionals=blocked_professionals, pending_professionals=pending_professionals, approved_professionals=approved_professionals, blocked_customers=blocked_customers, unblocked_customers=unblocked_customers)
#----------------Add category pages-----------------------------------

@app.route('/category/add')
@admin_reqd
def add_category():
    categories=Category.query.all()
    category_names = [category.name for category in categories]
    category_sizes = [len(category.services) for category in categories]

    return render_template('category/add.html', categories=categories, category_names=category_names, category_sizes=category_sizes)

@app.route('/category/add',methods=['POST'])
@admin_reqd
def add_category_post():
    name = request.form.get('name')
    if not name:
        flash('Please fill out the fields')
        return redirect(url_for('add_category'))
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    flash("Category added successfully")
    return redirect(url_for('add_category'))

@app.route('/category/<int:id>/')
@admin_reqd
def show_category(id):
    category=Category.query.get(id)
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin_db'))
    return render_template('category/show.html', category=category)
    #return("show category")

@app.route('/category/<int:id>/edit')
@admin_reqd
def edit_category(id):
    category=Category.query.get(id)
    
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin_db'))
    return render_template("category/edit.html", category=category)

@app.route('/category/<int:id>/edit', methods=['POST'])
@admin_reqd
def edit_category_post(id):
    category=Category.query.get(id)    
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin'))
    name=request.form.get('name')
    if not name:
        flash('Please fill out the fields')
        return redirect(url_for('edit_category',id=id))
    category.name=name
    db.session.commit()
    flash('Category updated successfully')  
    return redirect(url_for('admin_db'))
    

@app.route('/category/<int:id>/delete')
@auth_reqd
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin_db'))
    return render_template('category/delete.html', category=category)

@app.route('/category/<int:id>/delete', methods=['POST'])
@auth_reqd
def delete_category_post(id):
    category = Category.query.get(id)
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin_db'))
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully')
    return redirect(url_for('admin_db'))

#----------- Add services packages in a category-----------------------------------
@app.route('/service/add/<int:category_id>')
@admin_reqd
def add_service(category_id):
    category=Category.query.get(category_id)
    categories=Category.query.all() 
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin_db'))
    
    return render_template('service/add.html', category=category, categories=categories)

@app.route('/service/add/', methods=['POST'])
@admin_reqd
def add_service_post():
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    type = request.form.get('type')
    description = request.form.get('description')
    price = request.form.get('price')
    location = request.form.get('location')
    duration = request.form.get('duration')
    
    category = Category.query.get(category_id)

    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin_db'))
    if not name or not price or not type or not description or not location or not duration:
        flash('Please fill out the fields')
        return redirect(url_for('add_service', category_id=category_id))
    
    try:
    
        price=float(price)
        
    except ValueError:
        flash('price')
        return redirect(url_for('add_service', category_id=category_id))
    
    if price <= 0:
        flash('Price cannot be negative')
        return redirect(url_for('add_service', category_id=category_id))
    
    
    service = Service(name=name, price=price, category=category, type=type, description=description, location=location, duration=duration)
    db.session.add(service)
    db.session.commit()
    flash("Service added successfully")
    return redirect(url_for('show_category', id=category_id))



@app.route('/service/<int:id>/edit')
@admin_reqd
def edit_service(id):
    service=Service.query.get(id)
    categories=Category.query.all() 
    return render_template('service/edit.html', categories=categories,service=service)

@app.route('/service/<int:id>/edit', methods=['POST'])
@admin_reqd
def edit_service_post(id):
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    type = request.form.get('type')
    description = request.form.get('description')
    price = request.form.get('price')
    
    category = Category.query.get(category_id)
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin_db'))
    if not name or not price or not type or not description:
        flash('Please fill out the fields')
        return redirect(url_for('add_service', category_id=category_id))
    
    try:
        price=float(price)
        
    except ValueError:
        flash('Invalid quantity or price')
        return redirect(url_for('add_service', category_id=category_id))
    
    if price <= 0:
        flash('Quantity or price cannot be negative')
        return redirect(url_for('add_service', category_id=category_id))

    service=Service.query.get(id)
    service.name=name
    service.category=category
    service.type=type
    service.description=description
    service.price=price
    
    
    db.session.commit()
    flash("Service edited successfully")
    return redirect(url_for('show_category', id=category_id))

@app.route('/service/<int:id>/delete')
@admin_reqd
def delete_service(id):

    service = Service.query.get(id)
    if not service:
        flash('Service does not exist')
        return redirect(url_for('admin_db'))
    return render_template('service/delete.html', service=service)

@app.route('/service/<int:id>/delete', methods=['POST'])
@auth_reqd
def delete_service_post(id):
    service = Service.query.get(id)
    if not service:
        flash('Service does not exist')
        return redirect(url_for('admin_db'))
    category_id = service.category.id
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully')
    return redirect(url_for('show_category', id=category_id))

#-----------------professional pages-----------------------------------

# @app.route('/applybook')
# def applybook():
#     categories=Category.query.all()
#     category_names = [category.name for category in categories]
#     category_sizes = [len(category.services) for category in categories]

#     return render_template('applybook.html', categories=categories, category_names=category_names, category_sizes=category_sizes)

# -----------user-pages-----------------------------------
@app.route('/cust_db')
def cust_db():
    return render_template('cust_db.html')

@app.route('/catalogue')
@auth_reqd
def catalogue():
    #user_id in session/ if user id exists in session we will allow them to see catalogue.html
    #if user is an admin he goes to admin page else user page>> get user
    # user=User.query.get(session['user_id'])
    # if user.is_admin:
    #     return redirect(url_for('admin'))
    
    categories=Category.query.all()

    cname = request.args.get('cname') or ''
    sname = request.args.get('sname') or ''
    price = request.args.get('price')
    location = request.args.get('location') or ''
    datetime = request.args.get('datetime') or ''

    if price:
        try:
            price = float(price)
        except ValueError:
            flash('Invalid price')
            return redirect(url_for('catalogue'))
        if price <= 0:
            flash('Price cannot be negative')
            return redirect(url_for('catalogue'))

    if cname:
        categories = Category.query.filter(Category.name.ilike(f'%{cname}%')).all()
    return render_template('catalogue.html', categories=categories, cname=cname, sname=sname, price=price, location=location, datetime=datetime)

@app.route('/add_to_schedule/<int:service_id>', methods=['POST'])
@auth_reqd
def add_to_schedule(service_id):
    service = Service.query.get(service_id)
    if not service:
        flash('Service does not exist')
        return redirect(url_for('catalogue'))
    
    location = request.form.get('location')
    if not location:
        flash('Please enter location')
        return redirect(url_for('catalogue'))
    
    schedule_datetime_str = request.form.get('schedule_datetime')
    try:
        schedule_datetime = datetime.strptime(schedule_datetime_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash('Invalid date format')
        return redirect(url_for('catalogue'))
    
    if schedule_datetime < datetime.now():
        flash('Date & booking cannot be in the past')
        return redirect(url_for('catalogue'))
    
    schedule = Schedule.query.filter_by(service_id=service_id,schedule_datetime=schedule_datetime).first()
    if schedule:
        flash('Service already added to schedule')
        return redirect(url_for('catalogue'))
    else:
        schedule = Schedule(
            customer_id=session['user_id'], 
            service_id=service_id, 
            schedule_datetime=schedule_datetime, 
            location=location,
            is_pending=True,
            is_active=True,
            is_accepted=False,
            is_cancelled=False,
            is_completed=False
        )
            
       

        db.session.add(schedule)
    db.session.commit()
     
    flash('Service added to schedule successfully')
    return redirect(url_for('catalogue'))







# ------------------------routes from cust_db--------------------
@app.route('/schedule')
@auth_reqd
def schedule():
    user = User.query.get(session['user_id'])
    role_id = user.role_id
    if role_id == 2:
        professional = Professional.query.filter_by(user_id=session['user_id']).first()

        if not professional:
            flash('Professional does not exist')
            return redirect(url_for('login'))
    
        schedules = Schedule.query.join(Service).join(Category).filter(Category.name == professional.service_type).all()
        return render_template('view_appointments.html', schedules=schedules)
    
    elif role_id == 3:
            customer = Customer.query.filter_by(user_id=session['user_id']).first()

            if not customer:
                flash('Customer does not exist')
                return redirect(url_for('login'))
            schedules = Schedule.query.filter_by(customer_id=session['user_id']).all()
            schedules = Schedule.query.filter_by(customer_id=session['user_id']).all()
            return render_template('schedule.html', schedules=schedules)
    else:
        flash('You are not authorized to access this page')
        return redirect(url_for('home'))
        
        

@app.route('/schedule/<int:id>/delete', methods=['POST'])   
@auth_reqd
def delete_schedule(id):
    user = User.query.get(session['user_id'])
    role_id = user.role_id
    if role_id != 3:
        flash('You are not authorized to access this page')
        return redirect(url_for('home'))
    
    schedule = Schedule.query.get(id)        
    if schedule.customer_id != session['user_id']:
        flash('You do not have permission to delete this schedule')
        return redirect(url_for('schedule'))
    if schedule.customer_id != session['user_id']:
        flash('You do not have permission to delete this schedule')
        return redirect(url_for('schedule'))
    if schedule.is_accepted:
        flash('You cannot delete an accepted schedule')
        return redirect(url_for('schedule'))
    if schedule.is_cancelled:
        flash('Schedule already cancelled')
        return redirect(url_for('schedule'))
    if schedule.is_completed:
        flash('Schedule already completed')
        return redirect(url_for('schedule'))
    schedule.is_active = False
    schedule.is_cancelled = True
    
    
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully')
    return redirect(url_for('schedule'))
    

@app.route('/schedule/<int:id>/confirm', methods=['POST'])
@auth_reqd
def confirm(id):
    user = User.query.get(session['user_id'])
    role_id = user.role_id

    if role_id == 2:
        professional = Professional.query.filter_by(user_id=session['user_id']).first()
        if not professional:
            flash('Professional does not exist')
            return redirect(url_for('login'))
        
        schedule = Schedule.query.get(id)
        if not schedule or schedule.is_accepted:
            flash('No pending schedule to accept')
            return redirect(url_for('pending_booking'))
        
        transaction = Transaction(customer_id=schedule.customer_id, professional_id=professional.id, amount=0, datetime=datetime.now(), status='Accepted')
        service = Service.query.get(schedule.service_id)
        transaction.amount += float(service.price)

        booking = Booking(
            transaction=transaction,
            service=schedule.service,
            location=schedule.location,
            date_of_completion=schedule.schedule_datetime.date(),
            rating=None,
            remarks=None
        )
        db.session.add(booking)
        db.session.delete(schedule)
        db.session.add(transaction)
        db.session.commit()

        flash('Schedule accepted successfully')
        # return redirect(url_for('pending_booking'))
        return render_template('prof_booking.html',transactions=Transaction.query.filter_by(professional_id=professional.id).all())
                            
@app.route('/bookings')
@auth_reqd
def bookings():
    user = User.query.get(session['user_id'])
    role_id = user.role_id

    if role_id == 3:  # Customer
        cust_transactions = Transaction.query.filter_by(customer_id=session['user_id']).order_by(Transaction.datetime.desc()).all()
        return render_template('cust_bookings.html', transactions=cust_transactions)
    elif role_id == 2:  # Professional
        professional = Professional.query.filter_by(user_id=session['user_id']).first()
        if not professional:
            flash('Professional does not exist')
            return redirect(url_for('login'))
        
        prof_transactions = Transaction.query.filter_by(professional_id=professional.id).order_by(Transaction.datetime.desc()).all()
        print(prof_transactions)
        return render_template('prof_booking.html', transactions=prof_transactions)
    else:
        flash('You are not authorized to access this page')
        return redirect(url_for('home'))    

@app.route('/booking/<int:id>/delete', methods=['POST'])
@auth_reqd
def delete_booking(id):
    user = User.query.get(session['user_id'])
    role_id = user.role_id
    if role_id != 3:
        flash('You are not authorized to access this page')
        return redirect(url_for('home'))
    booking = Booking.query.get(id)
    if booking.transaction.customer_id != session['user_id']:
        flash('You do not have permission to delete this booking')
        return redirect(url_for('bookings'))
    if booking.transaction.status == 'Accepted':
        flash('You cannot delete an accepted booking')
        return redirect(url_for('bookings'))
    if booking.transaction.status == 'Cancelled':
        flash('Booking already cancelled')
        return redirect(url_for('bookings'))
    if booking.transaction.status == 'Completed':
        flash('Booking already completed')
        return redirect(url_for('bookings'))
    booking.transaction.status = 'Cancelled'
    db.session.commit()

    flash('Booking cancelled successfully')
    return redirect(url_for('bookings'))


@app.route('/booking/<int:id>/complete', methods=['POST'])
@auth_reqd
def complete_booking(id):
    user = User.query.get(session['user_id'])
    role_id = user.role_id
    if role_id != 3:
        flash('You are not authorized to access this page')
        return redirect(url_for('home'))
    booking = Booking.query.get(id)
    if booking.transaction.customer_id != session['user_id']:
        flash('You do not have permission to complete this booking')
        return redirect(url_for('bookings'))
    
    if booking.transaction.status == 'Cancelled':
        flash('Booking already cancelled')
        return redirect(url_for('bookings'))
    if booking.transaction.status == 'Completed':
        flash('Booking already completed')
        return redirect(url_for('bookings'))
    
    booking.transaction.date_of_completion = datetime.now()
    booking.transaction.status = 'Completed'
    db.session.commit()

    flash('Booking completed successfully')
    
    return redirect(url_for('bookings'))


@app.route('/booking/<int:id>/rate', methods=['POST'])
@auth_reqd
def rate_booking(id):
    user = User.query.get(session['user_id'])
    role_id = user.role_id
    if role_id != 3:
        flash('You are not authorized to access this page')
        return redirect(url_for('home'))
    transaction = Transaction.query.get(id)
    if transaction.customer_id != session['user_id']:
        flash('You do not have permission to rate this booking')
        return redirect(url_for('bookings'))
    if transaction.status != 'Completed':
        flash('You cannot rate a booking that is not completed')
        return redirect(url_for('bookings'))
    rating = request.form.get('rating')
    remarks = request.form.get('remarks')
    if not rating or not remarks:
        flash('Please fill out the fields')
        return redirect(url_for('bookings'))
    try:
        rating = int(rating)
    except ValueError:
        flash('Invalid rating')
        return redirect(url_for('bookings'))
    if rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5')
        return redirect(url_for('bookings'))
    booking = Booking.query.filter_by(transaction_id=id).first()
    booking.rating = rating
    booking.remarks = remarks
    db.session.commit()
    flash('Booking rated successfully')
    return redirect(url_for('bookings'))

#-----------------professional pages-----------------------------------
    
# ----booking request to professional-------------------   
@app.route('/pending_booking')
@auth_reqd
def pending_booking():
    professional = Professional.query.filter_by(user_id=session['user_id']).first()

    if not professional:
        flash('Professional does not exist')
        return redirect(url_for('login'))
    
    schedules = Schedule.query.join(Service).join(Category).filter(Category.name == professional.service_type).all()
    return render_template('view_appointments.html', schedules=schedules)


# route for accept appointment
@app.route('/accept_appointment/<int:id>', methods=['POST'])
@auth_reqd
def accept_appointment(id):
    schedule = Schedule.query.get(id)
    if not schedule:
        flash('Schedule does not exist')
        return redirect(url_for('pending_booking'))
    if schedule.is_accepted:
        flash('Schedule already accepted')
        return redirect(url_for('pending_booking'))
    if schedule.is_cancelled:
        flash('Schedule already cancelled')
        return redirect(url_for('pending_booking'))
    if schedule.is_completed:
        flash('Schedule already completed')
        return redirect(url_for('pending_booking'))
    schedule.professional_id = Professional.query.filter_by(user_id=session['user_id']).first().id
    schedule.is_accepted = True
    schedule.is_pending = False

    db.session.commit()
    db.session.delete(schedule)
    #delete from prof table
    flash('Schedule accepted successfully')



