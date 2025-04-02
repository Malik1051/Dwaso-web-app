from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

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
            cursor.execute("SELECT * FROM admin WHERE username = ? OR email = ?", (username_or_email, username_or_email))
            user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500
        
#  PRODUCTS
#Function to create the product table if it doesn't exist
def create_product_table():
    with sqlite3.connect('ecommerce.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Get and save products in product table
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def product_save():
    try:
        data = request.get_json()  # Get JSON data from the request
        print("Received data:", data)  # show response in console
        name = data.get('Product Name')
        price = data.get('Price (KES)')
        description = data.get('Description')
        image = data.get('Product Image')

        if not name or not price or not description or not image:
            return jsonify({"success": False, "message": "All fields are required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO product (name, price, description, image) VALUES (?, ?, ?, ?)",
                               (name, price, description, image))
                conn.commit()
                return jsonify({"success": True, "message": "Product uploaded successfully!"}), 201
            except sqlite3.IntegrityError:
                return jsonify({"success": False, "message": "Product already exists"}), 409
    
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500        

# Landing page
@app.route('/')
def index():
    return render_template('admin_login.html')

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

# Route for User pages
@app.route('/us_login', methods=['GET', 'POST'])
def us_login():
    return render_template('user_login.html')

@app.route('/us_signup', methods=['GET', 'POST'])
def us_signup():
    return render_template('user_signup.html')

# Run the application and create tables if they doesn't exist
if __name__ == '__main__':
    create_admin_table()  # Ensure the admin table exists
    create_user_table()  # Ensure the user table exists
    create_product_table()  # Ensure the user table exists
    app.run(host='0.0.0.0', port=5000)  # Use port 5000 for development
