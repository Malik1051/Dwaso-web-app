from flask import Flask, render_template, request, jsonify
import sqlite3
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

# Function to create the admin table if it doesn't exist
def create_admin_table():
    with sqlite3.connect('ecommerce.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Function to hash the password for security
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Function to check password validity
def check_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# Admin Login API
@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400

        # Connect to the database and fetch the admin credentials
        with sqlite3.connect('ecommerce.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
            admin = cursor.fetchone()

        if admin and check_password(admin['password'], password):
            return jsonify({"message": "Login successful", "admin_id": admin['id']}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# Route for the index page
@app.route('/')
def index():
    return render_template('login.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

# Run the application and create the table if it doesn't exist
if __name__ == '__main__':
    create_admin_table()  # Ensure the admin table exists
    app.run(host='0.0.0.0', port=5000)  # Use port 5000 for development
