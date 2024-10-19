from app import app
from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Role,Admin, Professional, Customer, Category, Service
from functools import wraps

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
        admin = Admin.query.filter_by(user_id=user.id).first()
        if admin:
            
            return redirect(url_for('admin_db', username=admin.user.username))
            
        else:
            return redirect(url_for('register_adb'))
 
    

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
    
    user = User.query.get(session['user_id'])
    professional= Professional.query.filter_by(user_id=user.id).first()
    if professional:
        #return ('already registered professional page' )
        return redirect(url_for('prof_db', name=professional.users.name))
    
    email = request.form['email']
    name = request.form['name']
    #username = request.form['username']
    contact = request.form['contact']
    service_type = request.form['service_type']
    experience = request.form['experience']
    
    
    #password    = request.form['password']
    if not email or not name or not contact or not service_type or not experience:
        flash('Please enter all the fields')
        return redirect(url_for('register_pdb'))
    
    new_professional = Professional(user_id=user.id, email=email, name=name, contact=contact, service_type=service_type, experience=experience)
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

#@app.route('/admin_db')
#def admin_db():
 #    return render_template('admin_db.html')
     

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
    # if user is admin, redirect to profile_admin page
    user = User.query.get(session['user_id'])
    role = Role.query.get(user.role_id)
    admin = Admin.query.filter_by(user_id=user.id).first()
    if role.name == 'Admin':
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
        return redirect(url_for('profile'))

#-------admin pages-----------------------------------





@app.route('/admin_db')
@admin_reqd
def admin_db():
    categories=Category.query.all()
    category_names = [category.name for category in categories]
    category_sizes = [len(category.services) for category in categories]

    return render_template('admin_db.html', categories=categories, category_names=category_names, category_sizes=category_sizes)
#-----------------category pages-----------------------------------

@app.route('/category/add')
@admin_reqd
def add_category():
    return render_template('category/add.html')

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
    return redirect(url_for('admin_db'))

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

#----------- services offered-----------------------------------
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
        flash('price')
        return redirect(url_for('add_service', category_id=category_id))
    
    if price <= 0:
        flash('Price cannot be negative')
        return redirect(url_for('add_service', category_id=category_id))
    
    
    service = Service(name=name, price=price, category=category, type=type, description=description)
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
@app.route('/applybook')
def applybook():
    categories=Category.query.all()
    category_names = [category.name for category in categories]
    category_sizes = [len(category.services) for category in categories]

    return render_template('applybook.html', categories=categories, category_names=category_names, category_sizes=category_sizes)

# -----------user-pages-----------------------------------

@app.route('/index')
@auth_reqd
def index():
    #user_id in session/ if user id exists in session we will allow them to see index.html
    #no checking needed now, bcoz we used decorator: auth reqd
    #if user is an admin he goes to admin page else user page>> get user
    user=User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    
    categories=Category.query.all()

    cname = request.args.get('cname') or ''
    sname = request.args.get('sname') or ''
    price = request.args.get('price')

    if price:
        try:
            price = float(price)
        except ValueError:
            flash('Invalid price')
            return redirect(url_for('index'))
        if price <= 0:
            flash('Price cannot be negative')
            return redirect(url_for('index'))

    if cname:
        categories = Category.query.filter(Category.name.ilike(f'%{cname}%')).all()
    return render_template('index.html', categories=categories, cname=cname, sname=sname, price=price) 

@app.route('/apply/<int:service_id>', methods=['POST'])
@auth_reqd
def apply(service_id):
    service = Service.query.get(service_id)
    if not service:
        flash('Service does not exist')
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    




@app.route('/view_user2')
@auth_reqd
def view_cust():
    return render_template('cust.html')

@app.route('/view_appointments')
def view_appointments():
    return render_template('appointments.html')

@app.route('/view_prof')
@auth_reqd
def view_prof():
    return render_template('prof.html')
@app.route('/add_prof')
@auth_reqd
def add_prof():
    return render_template('professional/add_prof.html')

@app.route('/flag_prof')
@auth_reqd
def flag_prof():
    return render_template('professional/flag_prof.html')
         

        
    
    

    
    
    