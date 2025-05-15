from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload directories if they don't exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'services'), exist_ok=True)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login first.')
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

# Function to create the product table if it doesn't exist
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

# Function to create the services table if it doesn't exist
def create_services_table():
    with sqlite3.connect('ecommerce.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                duration REAL NOT NULL,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/about')
def about():
    return render_template('about.html')


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
@app.route('/services', methods=['GET'])
def services():
    try:
        conn = get_db_connection()
        services = conn.execute('SELECT * FROM services ORDER BY created_at DESC').fetchall()
        conn.close()
        # Convert Row objects to dictionaries for easier access in Jinja
        services_list = []
        for service in services:
            services_list.append(dict(service))
        return render_template('services.html', services=services_list)
    except Exception as e:
        print(f"Error loading services: {str(e)}")
        # Return empty list if there's an error
        return render_template('services.html', services=[])

# Products page
@app.route('/products')
def products():
    try:
        conn = get_db_connection()
        # Get all products ordered by most recent first
        products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
        conn.close()
        return render_template('products.html', products=products)
    except Exception as e:
        print(f"Error loading products: {str(e)}")
        # Return empty list if there's an error
        return render_template('products.html', products=[])

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
    flash('You have been logged out.')
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
    session.pop('cart', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

# Route to get all services
@app.route('/admin/services', methods=['GET'])
@login_required
def get_services():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services ORDER BY created_at DESC")
            services = cursor.fetchall()
            
            # Convert services to list of dictionaries
            services_list = []
            for service in services:
                services_list.append({
                    'id': service['id'],
                    'name': service['name'],
                    'price': service['price'],
                    'duration': service['duration'],
                    'description': service['description'],
                    'image_path': service['image_path'],
                    'created_at': service['created_at']
                })
                
            return jsonify({'success': True, 'services': services_list})
            
    except Exception as e:
        print(f"Error fetching services: {str(e)}")
        return jsonify({'success': False, 'message': 'Error fetching services'}), 500

# Route to upload a new service
@app.route('/admin/upload-service', methods=['POST'])
@login_required
def upload_service():
    try:
        if 'serviceImage' not in request.files:
            return jsonify({'success': False, 'message': 'No image file provided'}), 400
            
        file = request.files['serviceImage']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
            
        # Save the image
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Save service details to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO services (name, price, duration, description, image_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                request.form.get('serviceName'),
                float(request.form.get('servicePrice')),
                float(request.form.get('serviceDuration')),
                request.form.get('serviceDescription'),
                filename
            ))
            conn.commit()
            
        return jsonify({'success': True, 'message': 'Service uploaded successfully'})
        
    except Exception as e:
        print(f"Error uploading service: {str(e)}")
        return jsonify({'success': False, 'message': 'Error uploading service'}), 500

# Route to delete a service
@app.route('/admin/services/<int:service_id>', methods=['DELETE'])
@login_required
def delete_service(service_id):
    try:
        with get_db_connection() as conn:
            # Get the image filename before deleting the service
            cursor = conn.cursor()
            cursor.execute("SELECT image_path FROM services WHERE id = ?", (service_id,))
            service = cursor.fetchone()
            
            if service:
                # Delete the image file
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], service['image_path'])
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # Delete the service from database
                cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
                conn.commit()
                
                return jsonify({'success': True, 'message': 'Service deleted successfully'})
            else:
                return jsonify({'success': False, 'message': 'Service not found'}), 404
                
    except Exception as e:
        print(f"Error deleting service: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting service'}), 500

# Add this new initialization function
def init_db():
    with get_db_connection() as conn:
        # Create admin table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,     
                password TEXT NOT NULL
            )
        ''')
        
        # Create user table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,     
                password TEXT NOT NULL
            )
        ''')
        
        # Create products table
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
        
        # Create services table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                duration REAL NOT NULL,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create bookings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                booking_date TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (service_id) REFERENCES services (id)
            )
        ''')
        
        conn.commit()

# Update the main block to use the new initialization
if __name__ == '__main__':
    # Initialize the database
    init_db()
    
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'services'), exist_ok=True)
    
    # Run the application
    app.run(debug=True) 

@app.route('/products/filter')
def filter_products():
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'newest')
    
    query = "SELECT * FROM products"
    params = []
    
    if category != 'all':
        query += " WHERE category = ?"
        params.append(category)
    
    if sort_by == 'newest':
        query += " ORDER BY created_at DESC"
    elif sort_by == 'price-low':
        query += " ORDER BY price ASC"
    elif sort_by == 'price-high':
        query += " ORDER BY price DESC"
    elif sort_by == 'name':
        query += " ORDER BY name ASC"
    
    conn = get_db_connection()
    products = conn.execute(query, params).fetchall()
    conn.close()
    
    # Convert products to list of dictionaries
    products_list = [{
        'id': p['id'],
        'name': p['name'],
        'price': float(p['price']),
        'description': p['description'],
        'image_path': p['image_path']
    } for p in products]
    
    return jsonify({'success': True, 'products': products_list})

@app.route('/cart/count')
def get_cart_count():
    cart = session.get('cart', [])
    return jsonify({'count': len(cart)})

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    if product:
        cart_item = {
            'id': product['id'],
            'name': product['name'],
            'price': float(product['price']),
            'quantity': 1
        }
        session['cart'].append(cart_item)
        session.modified = True
        return jsonify({'success': True, 'message': 'Product added to cart'})
    
    return jsonify({'success': False, 'message': 'Product not found'}) 
