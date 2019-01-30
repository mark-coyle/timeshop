from flask import Flask , render_template , request,redirect , flash , url_for , session, logging  , abort
from flask_mysqldb import MySQL
from flask_pymongo import PyMongo
from wtforms import Form , StringField, TextAreaField, PasswordField, SelectField , IntegerField , FileField  , validators
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename
from pymongo import MongoClient

import simplejson as json
import time , datetime , re , sys , os
app = Flask(__name__)

#Product Images
UPLOAD_FOLDER = os.path.dirname('static\images\products/')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# Database Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Wearables'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# init mysql
mysql =  MySQL(app)

#Mongop Config
client = MongoClient()
mongo_db = client.Wearables
newAdditions_collection = mongo_db['new_additions']
most_popular_collection = mongo_db['most_popular']

#Setup TTL
utc_time = datetime.datetime.utcnow()
newAdditions_collection.ensure_index("date" , expireAfterSeconds=3*60)
most_popular_collection.ensure_index("date" , expireAfterSeconds=3*60)


#Decorator for checking if users allowed access
def is_logged_in(f):
    @wraps(f)
    def wrap(*args , **kwargs):
        if 'logged_in' in session:
            return f(*args , **kwargs)
        else:
            flash('You currently do not have access to this area' , 'danger')
            return redirect(url_for('login'))
    return wrap


#Ensure user is Admin
def is_admin(f):
    @wraps(f)
    def wrap(*args , **kwargs):
        if session['user_type'] == "Admin":
            return f(*args , **kwargs)
        else:
            flash('You currently do not have admin access to this area' , 'danger')
            return redirect(url_for('home'))
    return wrap

#route decorater
def route(*a, **kw):
    kw['strict_slashes'] = kw.get('strict_slashes', False)
    return app.route(*a, **kw)

#decorater for files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/Home')
@is_logged_in
def home():
    # Get data for home dashboard
    cur = mysql.connection.cursor()
   # Check if product data is cached:
    if(newAdditions_collection.count() > 0 ):
        #Use Data from here
        res = newAdditions_collection.find({})
        new_additions = []

        for doc in res:
            product={}
            product['product_id'] = doc['product_id']
            product['name'] = doc['name']
            product['description'] = doc['description']
            product['price'] = doc['price']
            product['type'] = doc['type']
            product['image'] = doc['image']
            product['date_added'] = doc['date_added']
            new_additions.append(product)



    elif(newAdditions_collection.count() <= 0):
        # Cache doesn't exist

        #return user if username exists
        res = cur.execute("SELECT * FROM `products` ORDER BY `date_added` DESC LIMIT 5")
        new_additions = cur.fetchall()

        #push products to mongo
        for p in new_additions:
            p['date_added'] = datetime.datetime.date(p['date_added']).isoformat()
            #product = json.dumps(p)
            doc = {
                "product_id": p['product_id'],
                "name":p['name'],
                "description":p['description'],
                "type":p['type'],
                "price":p['price'],
                "image":p['image'],
                "date_added":p['date_added'],
                "date":utc_time
            }
            newAdditions_collection.insert_one(doc)


    #Check MongoDB Cache
    if(most_popular_collection.count() > 0):
        #Cache Exists
        product_count = most_popular_collection.count()
        res = most_popular_collection.find({})
        product_info = []

        for doc in res:
            product={}
            product['product_id'] = doc['product_id']
            product['name'] = doc['name']
            product['description'] = doc['description']
            product['like_count'] = doc['product_like_count']
            product_info.append(product)


    elif(most_popular_collection.count() <= 0):
        # Cache doesn't exist

        #Return Most popular Products
        product_count = cur.execute("SELECT `product_id` , COUNT(`product_id`) as `product_like_count` from `product_likes` GROUP BY `product_id` ORDER BY `product_like_count` DESC LIMIT 5")
        product_like_info = cur.fetchall()
          #If theres likes, get product info
        if product_count <= 0:
            products = 0

        #Get Product Details
        if product_count > 0:
            product_info = []
            #Foreach Product, Retrieve the Product Details
            #push products to mongo
            for p in product_like_info:
                cur.execute("Select * from `products` where `product_id` = %s" , [p['product_id']])
                current_product = cur.fetchone()
                current_product['like_count'] = p['product_like_count']
                doc = {
                    "product_id": current_product['product_id'],
                    "name": current_product['name'],
                    "description": current_product['description'],
                    "product_like_count":current_product['like_count'],
                    "date":utc_time

                }
                most_popular_collection.insert_one(doc)
                #Add Product to array
                product_info.append(current_product)





    return render_template('home.html' , new_additions = new_additions , products = product_info)




# Create Login Form
class LoginForm(Form):
    username = StringField('Username', [validators.length(min=4,max=20)])
    password = PasswordField('Password',
            [
                validators.data_required(),
            ])

#################################################                   Forms               #################################################
class AddProductForm(Form):
    name = StringField('Product Name', [validators.length(min=1,max=50)])
    product_type = SelectField('Product Type', coerce=int, choices=[(1, "Pocket Watches"), (2, "Modern Watches"), (3, "Classic Watches"), (4, "Smart Watches")], default = 1 ,)
    description = StringField('Product Description', [validators.length(min=4,max=300)])
    price = IntegerField('Product Price',[validators.data_required()])
    quantity = IntegerField('Product Quantity',[validators.data_required()])
    image = FileField('Product Image' )


class EditProductForm(Form):
    name = StringField('Product Name', [validators.length(min=1,max=50)])
    product_type = SelectField('Product Type',coerce=int, choices=[(1, "Pocket Watches"), (2, "Modern Watches"), (3, "Classic Watches"), (4, "Smart Watches")], default = 1 ,)
    description = StringField('Product Description', [validators.length(min=4,max=300)])
    price = IntegerField('Product Price',[validators.data_required()])
    quantity = IntegerField('Product Quantity')
    image = FileField('Product Image')


class RegisterForm(Form):
    first_name = StringField('First Name', [validators.length(min=1,max=50)])
    last_name = StringField('Last Name', [validators.length(min=1,max=50)])
    username = StringField('Username', [validators.length(min=4,max=20)])
    email = StringField('Email', [validators.data_required()])
    password = PasswordField('Password',
            [
                validators.data_required(),
                validators.EqualTo('confirm', message='Passwords do not match')
            ])
    confirm = PasswordField('Confirm Password')

class PasswordChangeForm(Form):
    current_password = PasswordField('Current Password', [validators.data_required()])
    new_password = PasswordField('New Password' ,
            [
                validators.data_required(),
                validators.EqualTo('confirm', message='Passwords do not match')
            ])
    confirm = PasswordField('Confirm Password')

class EditAccountForm(Form):
    first_name = StringField('First Name', [validators.length(min=1,max=50)])
    last_name = StringField('Last Name', [validators.length(min=1,max=50)])
    username = StringField('Username', [validators.length(min=4,max=20)])
    email = StringField('Email', [validators.data_required()])
    shipping_address = TextAreaField('Shipping Address' , [validators.input_required()])

class PasswordResetAdminForm(Form):
    password = PasswordField('Password', [validators.data_required()])


class ReviewForm(Form):
    title = StringField('Title', [validators.length(min=1,max=100)])
    description = TextAreaField('Review Content', [validators.length(min=1,max=1000)])




####################################################                                        ################################################

@app.route('/Control')
@is_admin
def Control():
    #get view data
    #Create cursor
    cur = mysql.connection.cursor()

    cur.execute("Select Count(*) as count from products")
    count = cur.fetchone()

    #Get total orders
    cur.callproc('getOrderTotal')
    order_total = cur.fetchone()


    #Get total users
    cur.execute("SELECT COUNT(*) as count from `accounts` where  `account_type` = %s" , ["User"])
    total_users = cur.fetchone()

    #Get Currently Logged In Users
    cur.execute("SELECT COUNT(*) as user_count from `accounts` where `logged_in` = %s" , [1])
    current_users = cur.fetchone()

    #Get Todays Orders
    todays_time = time.time()
    todays_timestamp = datetime.datetime.fromtimestamp(todays_time).strftime('%Y-%m-%d %H:%M:%S')

    cur.execute("SELECT COUNT(`order_id`) as orders from `log` where `log_time` = %s" , [todays_timestamp])
    todays_orders = cur.fetchone()

    #Get Average Users {Check Log Table For Logins With Timestamp And Divide}

    #Get Average Orders {Check Log Table For Orders With Timestamp And Divide}


    #commit to db
    mysql.connection.commit()

    #close connection
    cur.close()

    return render_template('views/control.html', count = count ,current_users = current_users , todays_orders = todays_orders , order_total = order_total , total_users = total_users)


@app.route('/Login', methods=['GET' , 'POST'])
def login():
    # Load in form
    form = LoginForm(request.form)
    # Check if get or post
    if request.method == "POST" and form.validate():
        #get username and password
        username = request.form['username']
        password = request.form['password']

        #Create cursor
        cur = mysql.connection.cursor()

        #return user if username exists
        cur.callproc('getUserByUsername' , [username])
        res = cur.fetchone()
        #res = cur.execute("SELECT * FROM users WHERE username = %s", [username])


        if res:
            #user exists , get password
            password_hashed = res['password']

            #Get users account details
            cur.execute("SELECT * FROM `accounts` where `user_id` = %s" , [res['user_id']])
            account = cur.fetchone()

            #Check if account is blocked
            if account['account_status'] != 0:
                error = 'This Account is currently Blocked'
                return render_template('login.html', error=error)

            #Check passwords match
            if sha256_crypt.verify(password, password_hashed):
                session['logged_in'] = True
                session['username'] = username
                session['user_id']  = res['user_id']
                session['user_type'] = account['account_type']
                session['account_id'] = account['account_id']

                #Get users Basket
                cur.execute("SELECT `basket_id` from `user_basket` where `user_id` = %s" , [res['user_id']])
                session['basket_id'] = cur.fetchone()

                #Update Logged In Status
                cur.execute("Update `accounts` set `logged_in` = %s where `account_id` = %s" , [1 , session['account_id']])

                #check User is admin
                if session['user_type'] == "Admin":
                    flash('You have successfully logged in', 'success')
                    return redirect(url_for('Control'))


                #update Log table
                user_id = res['user_id']
                # log = cur.execute("INSERT INTO `log`(`user_id` , `log_type` , `log_description`) VALUES(%s,%s,%s)" , [user_id , "Account" , username + " has logged in"])

                mysql.connection.commit()

                flash('You have successfully logged in', 'success')
                return redirect(url_for('home'))

            else:
                #passwords dont match
                error = 'Passwords do not match'
                return render_template('login.html', error=error)

            #close connection
            cur.close()

        else:
            # No username found
            error = 'That Username is currently not registered'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Login as Guest
@app.route('/Login/<string:guest>', methods=['GET' , 'POST'])
def Guest(guest):
    if(guest != "guest"):
        return redirect(url_for('login'))
    else:
        session['logged_in'] = True
        session['user_type'] = 'Guest'
        session['user_id'] = 0
        session['basket_id'] = 0
        return redirect(url_for('home'))


@app.route('/signup' ,methods=['GET' , 'POST'])
def signUp():
    # Load in form
    form = RegisterForm(request.form)

    # Check if get or post
    if request.method == "POST" and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        created_at_time = time.time()
        created_at = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')
        user_type = "User"


        #Create cursor
        cur = mysql.connection.cursor()


        #Preform Validation Checks
        cur.execute("SELECT * FROM `users` WHERE `username` = %s" , [username])
        username_check = cur.fetchone()

        if username_check:
            #Username already in use
            flash("This username is already in use, pick another" , 'warning')
            return redirect(url_for("signUp"))

        #Preform Validation Checks
        cur.execute("SELECT * FROM `users` WHERE `email` = %s" , [email])
        email_check = cur.fetchone()

        if email_check:
            #Email already in use
            flash("This email is already in use, pick another" , 'warning')
            return redirect(url_for("signUp"))

        #Validated Data , Continue

        #Create User
        res = cur.execute("INSERT INTO users(`first_name`,`last_name` , `username`,`email`, `password`) VALUES(%s, %s, %s,%s, %s )", (first_name,last_name,username,email,password))
        user = cur.lastrowid

        #Create User account
        res = cur.execute("INSERT INTO accounts(`user_id`,`created_at`,`account_type`) VALUES(%s, %s, %s)", (user , created_at,user_type))

        #get users ID
        if res:
            cur.execute("SELECT * FROM `users` where `username` = %s" , [username])
            user = cur.fetchone()



        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        #success message
        flash('Your Account Has been created', 'success')

        return redirect(url_for('login'))
    return render_template('signup.html', form = form)



@app.route('/Logout')
@is_logged_in
def logout():

        #Create cursor
        cur = mysql.connection.cursor()
        #Update Logged In Status

        cur.execute("UPDATE `accounts` set `logged_in` = %s where account_id = %s" , [0 , session['account_id']])

        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        #clear session
        session.clear()


        flash('You have been logged out', 'success')
        return redirect(url_for('login'))

@app.route('/Account')
@is_logged_in
def Account():
    form = PasswordChangeForm(request.form)
    user_id = session['user_id']

    #Get user details
    #Create cursor
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM users WHERE user_id = %s", [user_id])
    user = cur.fetchone()

    #Get users account details
    cur.execute("SELECT * FROM `accounts` where `user_id` = %s" , [user_id])
    account = cur.fetchone()

    #Get Users Orders
    order_count =  cur.callproc('getOrdersByUser' , [user_id])

    if order_count:
        orders = cur.fetchall()
        order_total = 0
        for order in orders:
            order_total += order['order_total']
    else:
        orders = 0
        order_total = 0


    #get users liked products
    liked_count = cur.execute("Select * from `product_likes` where `user_id` = %s" , [user_id])


    if liked_count > 0:
        liked_products = cur.fetchall()
        users_liked_products = []
        #Foreach Liked Product, Retrieve the Product Details
        for product in liked_products:
            cur.execute("Select * from `products` where `product_id` = %s" , [product['product_id']])
            current_product = cur.fetchone()

            #Add Product to array
            users_liked_products.append(current_product)

    else:
        users_liked_products = 0

    #Get Products in Basket
    basket_id = session['basket_id']

    #Check for basket_id , Admins wont have one
    if basket_id:
        users_basket = basket_id['basket_id']
    else:
        users_basket = False

    #If no basket
    if users_basket:
        basket_count = cur.execute("SELECT * FROM `basket_items` where `basket_id` = %s" , [users_basket])
    else:
        basket_count = 0



    if basket_count > 0:
        basket_items = cur.fetchall()
        users_basket_items = []
        #Foreach Product, Retrieve the Product Details
        for product in basket_items:
            cur.execute("Select * from `products` where `product_id` = %s" , [product['item_id']])
            current_product = cur.fetchone()
            current_product['quantity'] = product['quantity']

            #Add Product to array
            users_basket_items.append(current_product)

        #Get Basket Total
        total = 0
        for item in users_basket_items:
            total += item['price'] * item['quantity']

    else:
        users_basket_items = 0
        total = 0



    #close connection
    cur.close()

    return render_template('views/account.html' , user = user, account = account, orders = orders , liked_products = users_liked_products  , basket = users_basket_items, form = form , order_total = order_total,total = total )

@app.route('/password_change/<string:id>' , methods=['GET' , 'POST'])
@is_logged_in
def ChangePassword(id):
    form = PasswordChangeForm(request.form)
     #Validate ID
    if not (id is None):
        user_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    if request.method == "POST" and form.validate():
        current_password = form.current_password.data
        new_password = form.new_password.data

        #Check current password matches the one in database
        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE user_id = %s", [user_id])
        user = cur.fetchone()
        password_hashed = user['password']

        if sha256_crypt.verify(current_password, password_hashed):
            #passwords match
            password = sha256_crypt.encrypt(str(form.new_password.data))

            cur.execute('UPDATE `users` set `password` = %s WHERE `user_id` = %s' , [password , user_id])

            #commit to db
            mysql.connection.commit()

            #close connection
            cur.close()

            #success message
            flash('Your Password Has been updated', 'success')
            return redirect(url_for('logout'))

        else:
            #passwords dont match
            flash('Password Incorrect' , 'danger')
            return redirect(url_for('Account'))

    else:
        flash('Please Ensure All Fields Are Filled, and That your passwords match' , 'danger')
        return redirect(url_for('Account'))

@app.route('/EditAccount/<string:id>' , methods=['GET' , 'POST'])
@is_logged_in
def EditAccount(id):
    form = EditAccountForm(request.form)

    #Validate ID
    if not (id is None):
        user_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Pre Populate Form
    cur = mysql.connection.cursor()

    #Get users details
    cur.execute("Select * from `users` where user_id = %s", [user_id])
    user = cur.fetchone()

    #Get account details
    cur.execute("SELECT * from `accounts` where `user_id` = %s" , [user_id])
    account = cur.fetchone()

    #commit to db
    mysql.connection.commit()


    #Pre populate the form
    form.first_name.data = user['first_name']
    form.last_name.data = user['last_name']
    form.username.data = user['username']
    form.email.data = user['email']
    form.shipping_address.data = account['shipping_address']

    if request.method == "POST" and form.validate():
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        shipping_address = request.form['shipping_address']

        #Further Check for username, to ensure there is no other username the same

        if username != form.username.data:
            cur.execute("SELECT * FROM `users` where `username` = %s" , [username])
            result = cur.fetchone()

            if result:
                flash("That username is already taken" , 'danger')
                return redirect(url_for('EditAccount'))


        cur.execute("UPDATE `users` set `first_name` = %s , `last_name` = %s ,`username` = %s ,`email` = %s  where `user_id` = %s" , [first_name , last_name , username , email , user_id])
        #commit to db
        mysql.connection.commit()

        cur.execute("UPDATE `accounts` set `shipping_address` = %s where `user_id` = %s" , [shipping_address , user_id] )
        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        #success message
        flash('Your Account Has been Updated', 'success')

        return redirect(url_for('Account'))

    return render_template('views/account/edit.html', form = form)

@app.route('/DeleteAccount/<int:id>' , methods=['GET' , 'POST'])
@is_logged_in
def DeleteAccount(id):
    #ensure logged in user is deleting their own account
    user_id = session['user_id']
    basket = session['basket_id']
    basket_id = basket['basket_id']

    print(id)
    print(user_id)

    if(id != user_id):
        flash('You cant access this function currently. ' , 'danger')
        return redirect(url_for('Account'))
    else:
        #User deleting their own account

        #setup mysql
        cur = mysql.connection.cursor()

        #Remove users account
        cur.execute('DELETE FROM `accounts` where `user_id` = %s' , [user_id])

        #Remove users basket items
        cur.execute('DELETE FROM `basket_items` where `basket_id` = %s' , [basket_id])

        #Remove users basket
        cur.execute('DELETE FROM `user_basket` where `user_id` = %s' , [user_id])

        #Remove user from users table
        cur.execute('DELETE FROM `users` where `user_id` = %s' , [user_id])

        #Commit
        mysql.connection.commit()

        #Close mysql
        cur.close()
        session.clear()

        return redirect(url_for('login'))


@app.route('/Product/add',methods=['GET' , 'POST'])
@is_admin
def AddProduct():
    form = AddProductForm(request.form)

    # #Get Enum Select Values
    # #Create cursor
    # cur = mysql.connection.cursor()

    # cur.execute("SHOW COLUMNS FROM products LIKE 'type'")
    # values = cur.fetchone()
    # types = values['Type']



    # print("values" ,types)
    # #commit to db
    # mysql.connection.commit()

    # #close connection
    # cur.close()

    # Check if get or post
    if request.method == "POST" and form.validate():
        name = form.name.data
        product_type = form.product_type.data
        product_description = form.description.data
        product_price = form.price.data
        product_image = request.files[form.image.name]
        created_at_time = time.time()
        date_added = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')

        #Get quantity
        quantity = form.quantity.data

        if product_image and allowed_file(product_image.filename):
            filename = secure_filename(product_image.filename)
            product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #Create cursor
        cur = mysql.connection.cursor()

        #Validate this product doesn't exist
        cur.execute("SELECT * FROM `products` where name = %s" , [name])
        product_test = cur.fetchone()

        if product_test:
            flash('This product already exists' , 'warning')
            return redirect(url_for('ProductView' , id = product_test['product_id']))

        #create product
        cur.execute("INSERT INTO products(`name`,`type`,`description` , `price`, `image`, `date_added`) VALUES(%s, %s, %s, %s , %s, %s)", (name,product_type,product_description,product_price, filename,date_added))

        #get product id
        cur.execute("SELECT * FROM `products` where name = %s" , [name])
        product = cur.fetchone()

        #update quantity
        cur.execute("INSERT INTO `order_stock_levels`(`item_id` , `amount` , `stock_tolerance`) VALUES(%s , %s , %s) " , [product['product_id'] , quantity , 2])

        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        #success message
        flash('This Product has been added successfully', 'success')

        return redirect(url_for('StockList'))


    return render_template('views/product/add.html' , form = form )

@app.route('/Product/edit/<string:id>' , methods=['GET', 'POST'])
@is_admin
def ProductEdit(id):
    form = EditProductForm(request.form)
    #Validate ID
    if not (id is None):
        product_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Get Product Details
    cur = mysql.connection.cursor()

    cur.execute("Select * from products where product_id = %s", [product_id])
    product = cur.fetchone()

    #get quantity details
    cur.execute("Select * from order_stock_levels where item_id = %s" , [product['product_id']])
    quantity = cur.fetchone()

    #commit to db
    mysql.connection.commit()

    #close connection
    cur.close()

    #Pre populate the form
    form.name.data = product['name']
    form.description.data = product['description']
    form.price.data = product['price']
    form.quantity.data = quantity['amount']




    #Handle Product Update
    # Check if get or post
    if request.method == "POST" and form.validate():
        name = request.form['name']
        product_type = request.form['product_type']
        product_description = request.form['description']
        product_price = request.form['price']
        product_quantity = request.form['quantity']
        product_image = request.files[form.image.name]

        #parse file

        if product_image and allowed_file(product_image.filename):
            filename = secure_filename(product_image.filename)
            product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            #no image supplied re input file value
            filename = product['image']


        #Create cursor
        cur = mysql.connection.cursor()

        cur.execute("UPDATE `products` set `name` = %s , `type` = %s , `description`= %s , `price` = %s , `image` = %s WHERE `product_id` = %s" , [name , product_type , product_description , product_price , filename , product_id])

        #update stock quantity record
        cur.execute("UPDATE `order_stock_levels` set `amount` = %s where `item_id` = %s" , [product_quantity , product_id])
        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        #success message
        flash('This Product has been updated successfully', 'success')

        return redirect(url_for('StockList'))
    return render_template('views/product/edit.html' , product = product , form = form)

@app.route('/delete_product/<string:id>' , methods=['GET', 'POST'])
@is_admin
def delete_product(id):
    #Validate ID
    if not (id is None):
        product_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

     #Create cursor
    cur = mysql.connection.cursor()

    cur.execute("DELETE from `products` where product_id = %s", [product_id])
    #commit to db
    mysql.connection.commit()

    #close connection
    cur.close()

    flash("This Product has been Deleted" , "success")
    return redirect(url_for('StockList'))


@app.route('/Product/view/<string:id>' , methods =['GET' , 'POST'])
def ProductView(id):
    #Validate ID
    if not (id is None):
        product_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not id.isnumeric():
        abort(404)
     #Get Product Details
    cur = mysql.connection.cursor()

    cur.execute("Select * from products where product_id = %s", [product_id])
    product = cur.fetchone()

    #Pass user details
    user_id = session['user_id']
    cur.execute("Select * from `users` where `user_id` = %s" , [user_id])
    user = cur.fetchone()

    #Get Basket ID from Session
    basket_id = session['basket_id']

    if basket_id:
        users_basket = basket_id['basket_id']
    else:
        users_basket = False

    #Check if Item is in Cart
    cur.execute("SELECT * FROM `basket_items` where `basket_id` = %s AND `item_id` = %s" , [users_basket , product_id])
    basket_items = cur.fetchone()

    if basket_items:
        #Currently in Cart
        item_in_cart = True
    else:
        #not in cart
        item_in_cart = False


    #Check if user has liked this product
    cur.execute("SELECT * FROM `product_likes` WHERE `user_id` = %s AND `product_id` = %s" , [user_id , product_id])
    res = cur.fetchone()

    if res:
        #User has liked this product
        user_liked = True
    else:
        user_liked = False

    #Get Count of Product Likes
    cur.execute("SELECT COUNT(`product_id`) as `product_like_count` from `product_likes` where `product_id` = %s" , [product_id])
    like_count = cur.fetchone()

    #Check how many times product has been ordered
    cur.execute("SELECT COUNT(`item_id`) as `order_count` from `order_items` where `item_id` = %s" , [product_id])
    order_count = cur.fetchone()

    #Get Similar Products
    cur.execute("SELECT * from `products` where `type` = %s and `product_id` != %s LIMIT 3" , [product['type'] , product_id])
    similar_list = cur.fetchall()

    #Get Review Information
    cur.execute("SELECT * from `reviews` where `product_id` = %s ORDER BY `datetime` DESC LIMIT 5" , [product_id])
    reviews_list = cur.fetchall()

    #Validate
    if reviews_list:
        reviews = reviews_list
        for review in reviews:
            cur.execute("SELECT * FROM `users` where `user_id` = %s" , [review['user_id']])
            current_user = cur.fetchone()
            review['username'] = current_user['username']
    else:
        reviews = False

    #Check product quantity
    cur.execute("SELECT * FROM `order_stock_levels` where `item_id` = %s" , [product_id])
    stock = cur.fetchone()



    #commit to db
    mysql.connection.commit()

    #close connection
    cur.close()

    return render_template('views/product/view.html', product = product ,reviews = reviews, stock = stock,user = user , user_liked = user_liked ,like_count = like_count, order_count = order_count,item_in_cart = item_in_cart , similar_products = similar_list)


#Route For Liking Product
@app.route('/LikeProduct/<string:user_id>/<string:product_id>' , methods=['GET', 'POST'])
@is_logged_in
def LikeProduct(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Validate ID's Preform Like Request
    cur = mysql.connection.cursor()
    created_at_time = time.time()
    liked_at = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')
    #Get Todays date


    cur.execute("INSERT INTO  `product_likes` (`product_id` , `user_id` , `date_liked`) VALUES(%s , %s , %s)" , [product_id , user_id, liked_at])
    # cur.execute("INSERT INTO `log`(`user_id` , `log_type` , `log_description` , `product_id`) VALUES(%s,%s,%s, %s)" , [user_id , "Stock" , "Product Liked", product_id])

    mysql.connection.commit()

    cur.close()

    return redirect(url_for('ProductView' , id = product_id))

#Route For Unliking Product
@app.route('/UnlikeProduct/<string:user_id>/<string:product_id>' , methods=['GET', 'POST' , 'DELETE'])
@is_logged_in
def UnlikeProduct(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Validate ID's Preform Like Request
    cur = mysql.connection.cursor()
    created_at_time = time.time()
    liked_at = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')
    #Get Todays date


    cur.execute("DELETE from `product_likes` WHERE `user_id` = %s AND `product_id` = %s" , [user_id , product_id])

    mysql.connection.commit()

    cur.close()

    return redirect(url_for('ProductView' , id=  product_id))

#Product Review:
@app.route("/Product/review/<string:product_id>/<string:user_id>" , methods = ['GET' , 'POST'])
@is_logged_in
def Review(product_id , user_id):
    #Validate Inputs
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'User ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Check if user has already submitted a Review
    #preprare mysql
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM `reviews` where user_id = %s AND product_id = %s" , [user_id , product_id])
    reviewed = cur.fetchone()


    if reviewed:
        #Already Reviewed , redirect
        flash('You have already reviewed this product' , 'warning')
        return redirect(url_for('ProductView' , id=  product_id))

    #Get Review Form
    form = ReviewForm(request.form)

    #Handle Submission
    if request.method == "POST" and form.validate():
        title = form.title.data
        description = form.description.data
        reviewed_time = time.time()
        review_date = datetime.datetime.fromtimestamp(reviewed_time).strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("INSERT INTO `reviews`(`title` , `description` , `datetime` , `user_id` , `product_id`) VALUES(%s,%s,%s,%s,%s)" , [title , description , review_date , user_id , product_id])

        #commit query
        mysql.connection.commit()

        #close db connection
        cur.close()

        #redirect
        return redirect(url_for('ProductView' , id=  product_id))



    return render_template('views/product/review.html' , form = form )


#Add to Cart
@app.route('/AddToCart/<string:user_id>/<string:product_id>' , methods=['GET', 'POST'])
@is_logged_in
def AddToCart(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Insert Item into Basket_items
    cur = mysql.connection.cursor()

    #Get Users Basket ID
    basket_id =  session['basket_id']
    users_basket = basket_id['basket_id']

    cur.execute("INSERT INTO `basket_items`(`basket_id` , `item_id`) VALUES(%s , %s)" , [users_basket , product_id])

    cur.execute("INSERT INTO `log`(`user_id` , `log_type` , `log_description` , `product_id`) VALUES(%s,%s,%s, %s)" , [user_id , "Stock" , "Product Added to Cart", product_id])

    mysql.connection.commit()

    cur.close()


    return redirect(url_for('ProductView' , id=  product_id))

#Remove From Cart
@app.route('/RemoveFromCart/<string:user_id>/<string:product_id>' , methods=['GET', 'POST' , 'DELETE'])
@is_logged_in
def RemoveFromCart(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'User ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Insert Item into Basket_items
    cur = mysql.connection.cursor()

    #Get Users Basket ID
    basket_id =  session['basket_id']
    users_basket = basket_id['basket_id']

    cur.execute("DELETE From `basket_items` where `basket_id` = %s AND  `item_id` = %s" , [users_basket , product_id])

    mysql.connection.commit()

    cur.close()


    return redirect(url_for('ProductView' , id=  product_id))

#Increase Quantity
@app.route('/IncreaseQuantity/<string:user_id>/<string:product_id>' , methods=['GET', 'POST'])
@is_logged_in
def IncreaseQuantity(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'User ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Insert Item into Basket_items
    cur = mysql.connection.cursor()

    #Get Users Basket ID
    basket_id =  session['basket_id']
    users_basket = basket_id['basket_id']

    cur.execute("UPDATE `basket_items` set `quantity` = `quantity` + 1 where `basket_id` = %s AND `item_id` = %s" , [users_basket , product_id])

    mysql.connection.commit()

    cur.close()


    return redirect(url_for('Account'))


#Remove From Cart
@app.route('/DecreaseQuantity/<string:user_id>/<string:product_id>' , methods=['GET', 'POST'])
@is_logged_in
def DecreaseQuantity(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'User ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Insert Item into Basket_items
    cur = mysql.connection.cursor()

    #Get Users Basket ID
    basket_id =  session['basket_id']
    users_basket = basket_id['basket_id']

    cur.execute("UPDATE `basket_items` set `quantity` = `quantity` - 1 where `basket_id` = %s AND `item_id` = %s" , [users_basket , product_id])

    mysql.connection.commit()

    cur.close()


    return redirect(url_for('Account'))



#Route For Showing Stock List
@app.route('/StockList')
@is_admin
def StockList():
    #Get Product List
    cur = mysql.connection.cursor()

    product_count = cur.execute("Select * from products")


    #Get Quantitys For products
    if product_count > 0:
        products = cur.fetchall()
        stock_items = []
    #Foreach Product, Retrieve the Product Details
    for product in products:
        cur.execute("Select * from `order_stock_levels` where `item_id` = %s" , [product['product_id']])
        current_product = cur.fetchone()
        product['quantity'] = current_product['amount']
        product['tolerance'] = current_product['stock_tolerance']
        if product['quantity'] < product['tolerance']:
            product['stock_status'] = 'Under Tolerance'

        else:
            product['stock_status'] = 'Above Tolerance'
        #Add Product to array
        stock_items.append(product)



    #Logic for Stock Issues

    #commit to db
    mysql.connection.commit()

    #close connection
    cur.close()

    return render_template('views/product/list.html' , product_list = stock_items)



@app.route('/UserManager' , methods=['GET', 'POST'])
@is_admin
def UserManager():
    #Get All Users
    cur = mysql.connection.cursor()
    account_list = cur.execute("SELECT * FROM `accounts` WHERE `account_type` = %s" , ["User"])
    accounts = cur.fetchall()

    #Get Users
    user_list  = []
    for i in accounts:
        cur.execute("SELECT * FROM `users` where `user_id` = %s" , [i['user_id']])
        user = cur.fetchone()
        i['username'] = user['username']
        user_list.append(i)


    cur.close()

    return render_template('views/admin/usermanager.html' , users = user_list)



@app.route('/BlockAccount/<string:id>' , methods = ['GET','POST'])
@is_admin
def BlockAccount(id):
     #Validate ID
    if not (id is None):
        user_id = id
    else:
         error = 'User ID is invalid'
         return render_template('views/admin/usermanager.html', error=error)


    cur = mysql.connection.cursor()
    cur.execute("UPDATE `accounts` set `account_status` = 1 where user_id = %s" , [user_id])

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('UserManager'))


@app.route('/UnblockAccount/<string:id>' , methods = ['GET','POST'])
@is_admin
def UnblockAccount(id):
     #Validate ID
    if not (id is None):
        user_id = id
    else:
         error = 'User ID is invalid'
         return render_template('views/admin/usermanager.html', error=error)


    cur = mysql.connection.cursor()
    cur.execute("UPDATE `accounts` set `account_status` = 0 where user_id = %s" , [user_id])

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('UserManager'))

@app.route('/ResetPassword/<string:id>' , methods = ['GET','POST'])
@is_admin
def PasswordResetAdmin(id):
    form = PasswordResetAdminForm(request.form)
     #Validate ID
    if not (id is None):
        user_id = id
    else:
         error = 'User ID is invalid'
         return render_template('views/admin/usermanager.html', error=error)

    cur = mysql.connection.cursor()
    #pass user details to view
    cur.execute("SELECT * FROM `users` where `user_id` = %s", [user_id])
    user = cur.fetchone()

    #Check if it matches current password
    current_password = user['password']
    password_reset = sha256_crypt.encrypt(str(form.password.data))

    if sha256_crypt.verify(current_password, password_reset):
         error = 'Passwords cannot remain the same'
         return render_template('views/admin/usermanager.html', error=error)


    cur.execute("UPDATE `users` set `password` = %s where user_id = %s" , [password_reset , user_id])

    mysql.connection.commit()
    cur.close()


    return render_template('views/admin/passwordreset.html' , form = form , user = user)


@app.route('/Checkout' , methods = ['GET' , 'POST'])
@is_logged_in
def Checkout():
    #Get the Users Details
    user_id = session['user_id']
    user_basket = session['basket_id']

    basket_id = user_basket['basket_id']



    #Get Items in user basket
    cur = mysql.connection.cursor()
    item_count = cur.execute("SELECT * FROM `basket_items` where `basket_id` = %s" , [basket_id])


    #If user has no items, redirect
    if item_count <= 0:
        flash("You Currently Have No Items to Checkout" , "danger")
        return redirect(url_for("Account"))

    #Get Item Details
    if item_count > 0:
        basket_items = cur.fetchall()
        users_basket_items = []
    #Foreach Product, Retrieve the Product Details
    for product in basket_items:
        cur.execute("Select * from `products` where `product_id` = %s" , [product['item_id']])
        current_product = cur.fetchone()
        current_product['quantity'] = product['quantity']
        #Add Product to array
        users_basket_items.append(current_product)
    #Get Basket Total
    total = 0
    for item in users_basket_items:
         total += item['price'] * item['quantity']


    #Get Users Details
    cur.execute("SELECT * FROM `users` where `user_id` = %s" , [user_id])
    user = cur.fetchone()

    #get account details
    cur.execute("SELECT * FROM `accounts` where `user_id` = %s" , [user_id])
    account = cur.fetchone()


    mysql.connection.commit()
    cur.close()

    return render_template("views/account/checkout.html" , products = users_basket_items , total = total , user = user , account = account)


@app.route('/ConfirmOrder' , methods = ['GET' , 'POST'])
@is_logged_in
def ConfirmOrder():
    #Create Mysql cursor
    cur = mysql.connection.cursor()

    #Get Users Details:
    user_id = session['user_id']
    users_basket = session['basket_id']
    basket_id = users_basket['basket_id']

    cur.execute("SELECT * FROM `users` where `user_id` = %s" , [user_id])
    user = cur.fetchone()

    cur.execute("SELECT * FROM `accounts` where `user_id` = %s" , [user_id])
    account = cur.fetchone()


    #Set Order Date To Today
    created_at_time = time.time()
    order_date = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')

    #Get Basket Items
    cur = mysql.connection.cursor()
    item_count = cur.execute("SELECT * FROM `basket_items` where `basket_id` = %s" , [basket_id])

    #If user has no items, redirect
    if item_count <= 0:
        flash("You Currently Have No Items to Checkout" , "danger")
        return redirect(url_for("Account"))

    #Get Item Details
    if item_count > 0:
        basket_items = cur.fetchall()
        order_items = []

    #Foreach Product, Retrieve the Product Details
    for product in basket_items:
        cur.execute("Select * from `products` where `product_id` = %s" , [product['item_id']])
        current_product = cur.fetchone()
        current_product['quantity'] = product['quantity']
        #Add Product to array
        order_items.append(current_product)


    #Calculate Order Total
    order_total = 0
    for item in order_items:
        order_total += item['price'] * item['quantity']
        #Update Stock Levels
        cur.execute("UPDATE `order_stock_levels` set `amount` = `amount` - %s where `item_id` = %s " , [item['quantity'] , item['product_id']])



    #Update Order Table
    cur.execute("INSERT INTO `orders`(`order_total` , `order_date` , `shipping_address` , `user_id`) VALUES(%s, %s, %s ,%s)" , [order_total,order_date,account['shipping_address'],user_id])

    #Get Order ID
    cur.execute("SELECT * from `orders` where  `user_id` = %s AND `order_date` = %s" , [user_id, order_date])
    order_id = cur.fetchone()

    for item in order_items:
        #Update Order Items
        cur.execute("INSERT INTO `order_items`(`item_id`,`order_id`) VALUES(%s, %s)" , [item['product_id'] , order_id['order_id']])

    #Reset Users Basket
    cur.execute("DELETE FROM `basket_items` where `basket_id` = %s" , [basket_id])

    #update log table

    cur.execute("INSERT INTO `log`(`user_id` , `order_id`,`log_type` , `log_description` ) VALUES(%s,%s,%s,%s)" , [user_id , order_id['order_id'] ,"Order" , "Order Completed"])


    mysql.connection.commit()
    cur.close()

    return redirect(url_for('Account'))


# Product Category Views
@app.route('/<string:name>' , methods = ['GET' , 'POST'])
@is_logged_in
def Category(name):
    #Validate name
    if name == '':
        flash('The Product Type Is incorrect' , 'warning')
        return redirect(url_for('Home'))

    acceptable_urls = ['ClassicWatches','ModernWatches','SmartWatches','PocketWatches']
    if name not in acceptable_urls:
        flash('The Product Type Is incorrect' , 'warning')
        abort(404)

    #Add space to category type
    name = name.replace("Watches" , " Watch")

    #Setup Cursor
    cur = mysql.connection.cursor()
    cur.callproc('getProductsByType' , [name])
    results = cur.fetchall()

    return render_template('views/product/category.html' , watches = results)


@app.route('/GetProductLikes' , methods=['GET'])
@is_admin
def GetProductLikes():
    #get the like data return as json.

    #mysql
    cur = mysql.connection.cursor()
    cur.execute("SELECT `product_id`, COUNT(`product_id`) as likes FROM `product_likes` Group BY `product_id` ")
    like_list = cur.fetchall()

    #get product names and types
    #empty like list
    likes = []
    for product in like_list:
        cur.execute("Select `name` , `type` from `products` where `product_id` = %s", [product['product_id']])
        current_product = cur.fetchone()
        current_product['amount'] = product['likes']
        #add to new list
        likes.append(current_product)

    #Return Data in Correct Format
    likes = json.dumps(likes)
    cur.close()

    return likes


@app.route('/GetOrderData' , methods=['GET'])
@is_admin
def GetOrderData():
    #mysql
    cur = mysql.connection.cursor()

    cur.execute("SELECT `order_total` , `order_date` from `orders` ")
    data = cur.fetchall()

    #Group Orders By Months
    cur.execute("SELECT month(`order_date`) as `month` , SUM(`order_total`) as `month_total` from `orders` GROUP BY month(`order_date`)")
    totals = cur.fetchall()

    #add month_orders to totals
    total_test = []
    for key in totals:
        #Create Nested Orders Array
        key['orders'] = []
        cur.execute("SELECT `order_total` , `order_date` from `orders` where month(`order_date`) = %s" , [key['month']])
        #Get Month Name From number
        key['month'] = datetime.date(1900, key['month'], 1).strftime('%B')
        orders = cur.fetchall()
        for order in orders:
            order['order_date'] = datetime.datetime.date(order['order_date']).isoformat()
            key['orders'].append(order)

        total_test.append(key)



    #Format Data
    for d in data:
        d['order_date'] = datetime.datetime.date(d['order_date']).isoformat()


    cur.close()

    data = json.dumps(total_test)
    return data



@app.route('/OrderReport' , methods = ['GET' , 'POST'])
@is_admin
def OrderReport():

    order_data = []
    #Get All Months That have Orders
    #Create Sql
    cur = mysql.connection.cursor()
    cur.execute("SELECT month(`order_date`) as months from `orders` group by months")
    data = cur.fetchall()

    #convert to month name
    for i in data:
        #Get Month Name From number
        i['month_value'] = i['months']
        i['months'] = datetime.date(1900, i['months'] , 1).strftime('%B')

    cur.close()

    if request.method == "POST":
        #Handle User Input
        month_chosen = request.form.get('month')


        #Create Sql
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from `orders` WHERE month(`order_date`) =%s" , [month_chosen])
        orders = cur.fetchall()

        #get user data & order item data
        order_data = []
        for i in orders:
            cur.execute("SELECT * FROM `users` where `user_id` = %s" ,[i['user_id']] )
            current_user = cur.fetchone()

            cur.execute("SELECT * FROM `accounts` where `user_id` = %s" ,[i['user_id']])
            current_account = cur.fetchone()
            # cur.execute("SELECT * from `order_items` where `order_id` = %s" ,[i['order_id']] )
            # current_item = cur.fetchone()

            #Get item details
            # cur.execute("SELECT * from `products` where `product_id` = %s" , [current_item['item_id']])
            # item_info = cur.fetchone()

            i['fname'] = current_user['first_name']
            i['lname'] = current_user['last_name']
            i['shipped_to'] = current_account['shipping_address']
            # i['item_name'] = item_info['name']
            # i['item_description'] = item_info['description']
            order_data.append(i)



        cur.close()


    return render_template('views/admin/report.html' , data = data , orders = order_data )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.secret_key= ''
    app.run()
