from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('ad_login'))
        return f(*args, **kwargs)
    return decorated_function

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('ecommerce.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

#                     ADMINISTRATOR
# Function to create the admin table if it doesn't exist
def create_admin_table():
    with sqlite3.connect('ecommerce.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,     
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

#Admin signup
@app.route('/admin/signup', methods=['POST'])
def admin_signup():
    try:
        data = request.get_json()  # Get JSON data from the request
        print("Received data:", data)  # show response in console
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"success": False, "message": "All fields are required"}), 400
        
        hashed_password = generate_password_hash(password)  # Hash the password

        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO admin (username, email, password) VALUES (?, ?, ?)",
                               (username, email, hashed_password))
                conn.commit()
                return jsonify({"success": True, "message": "Account created successfully!"}), 201
            except sqlite3.IntegrityError:
                return jsonify({"success": False, "message": "Username or email already exists"}), 409
    
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500


# Admin Login 
@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')

        if not username_or_email or not password:
            return jsonify({"success": False, "message": "Username/Email and password are required"}), 400

        # Connect to the database and fetch the admin credentials
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE username = ? OR email = ?", (username_or_email, username_or_email))
            admin = cursor.fetchone()

        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['id']
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500
    

#                    USER    
#Function to create the admin table if it doesn't exist
def create_user_table():
    with sqlite3.connect('ecommerce.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,     
                password TEXT NOT NULL
            )
        ''')
        conn.commit()


#User signup
@app.route('/user/signup', methods=['POST'])
def user_signup():
    try:
        data = request.get_json()  # Get JSON data from the request
        print("Received data:", data)  # show response in console
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"success": False, "message": "All fields are required"}), 400
        
        hashed_password = generate_password_hash(password)  # Hash the password

        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                               (username, email, hashed_password))
                conn.commit()
                return jsonify({"success": True, "message": "Account created successfully!"}), 201
            except sqlite3.IntegrityError:
                return jsonify({"success": False, "message": "Username or email already exists"}), 409
    
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500


# User Login 
@app.route('/user/login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')

        if not username_or_email or not password:
            return jsonify({"success": False, "message": "Username/Email and password are required"}), 400

        # Connect to the database and fetch the admin credentials
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username = ? OR email = ?", (username_or_email, username_or_email))
            user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500
        
#                              PRODUCTS
# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

#Function to create the product table if it doesn't exist
def create_products_table():
    with sqlite3.connect('ecommerce.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit() 

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle product upload
@app.route('/admin/upload-product', methods=['POST'])
@login_required
def upload_product():
    try:
        if 'productImage' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
            
        file = request.files['productImage']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
            
        if file and allowed_file(file.filename):
            # Create a secure filename and save the file
            filename = secure_filename(file.filename)
            # Add timestamp to filename to prevent duplicates
            filename = f"{int(time.time())}_{filename}"
            
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Get other form data
            product_name = request.form.get('productName')
            product_price = request.form.get('productPrice')
            product_description = request.form.get('productDescription')
            
            # Validate form data
            if not product_name or not product_price:
                # Remove uploaded file if form data is invalid
                os.remove(file_path)
                return jsonify({'success': False, 'message': 'Product name and price are required'}), 400
            
            # Save product details to database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (name, price, description, image_path)
                    VALUES (?, ?, ?, ?)
                """, (
                    product_name,
                    float(product_price),
                    product_description,
                    filename
                ))
                conn.commit()
                
            return jsonify({
                'success': True, 
                'message': 'Product uploaded successfully',
                'product': {
                    'name': product_name,
                    'price': product_price,
                    'description': product_description,
                    'image': filename
                }
            })
            
        return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error uploading product: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while uploading the product'}), 500

# Route to get all products
@app.route('/admin/products', methods=['GET'])
@login_required
def get_products():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
            products = cursor.fetchall()
            
            # Convert products to list of dictionaries
            products_list = []
            for product in products:
                products_list.append({
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'description': product['description'],
                    'image_path': product['image_path'],
                    'created_at': product['created_at']
                })
                
            return jsonify({'success': True, 'products': products_list})
            
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return jsonify({'success': False, 'message': 'Error fetching products'}), 500          

#       CART
# Add a product to the cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    session['cart'] = cart
    return redirect(url_for('view_cart'))

#View Cart
@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    return render_template('cart.html', cart=cart)

#Remove products from cart
@app.route('/remove_from_cart/<product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
    return redirect(url_for('view_cart'))

# Clear Cart
@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))


# Landing page
@app.route('/')
def index():
    return render_template('index_landing.html')

# Services page
@app.route('/services', methods=['GET', 'POST'])
def services():
    return render_template('services.html')

# Products page
@app.route('/products')
def products():
    return render_template('products.html')

# Route for Admin pages
@app.route('/ad_login', methods=['GET', 'POST'])
def ad_login():
    return render_template('admin_login.html')

@app.route('/ad_signup', methods=['GET', 'POST'])
def ad_signup():
    return render_template('admin_signup.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html') 

# Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('ad_login'))

#Route for user pages
@app.route('/us_login', methods=['GET', 'POST'])
def us_login():
    return render_template('user_login.html')

@app.route('/us_signup', methods=['GET', 'POST'])
def us_signup():
    return render_template('user_signup.html')

# Logout
@app.route('/user/logout')
def user_logout():
    session.pop('user_id', None)
    return redirect(url_for('us_login'))

# Run the application and create tables if they doesn't exist
if __name__ == '__main__':
    create_admin_table()
    create_products_table()
    create_user_table()
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000)  # Use port 5000 for development
