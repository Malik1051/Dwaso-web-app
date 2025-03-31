from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('ecommerce.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

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
    
    

# Route for the index page
@app.route('/')
def index():
    return render_template('admin_login.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('admin_login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('admin_signup.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html') 

# Route for Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('login'))

# Run the application and create the table if it doesn't exist
if __name__ == '__main__':
    create_admin_table()  # Ensure the admin table exists
    app.run(host='0.0.0.0', port=5000)  # Use port 5000 for development
