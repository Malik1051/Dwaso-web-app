from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flashing messages

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directories exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'services'), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

# Admin Routes for Product Management
@app.route('/admin/upload-product', methods=['POST'])
def upload_product():
    if 'productImage' not in request.files:
        flash('No file uploaded')
        return redirect(request.url)
    
    file = request.files['productImage']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', filename)
        file.save(file_path)
        
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price, description, image_path) VALUES (?, ?, ?, ?)',
                    (request.form['productName'],
                     request.form['productPrice'],
                     request.form['productDescription'],
                     'uploads/products/' + filename))
        conn.commit()
        conn.close()
        
        flash('Product uploaded successfully!')
        return jsonify({'success': True})
    
    flash('Invalid file type')
    return jsonify({'success': False})

# Admin Routes for Service Management
@app.route('/admin/upload-service', methods=['POST'])
def upload_service():
    if 'serviceImage' not in request.files:
        flash('No file uploaded')
        return redirect(request.url)
    
    file = request.files['serviceImage']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'services', filename)
        file.save(file_path)
        
        conn = get_db_connection()
        conn.execute('INSERT INTO services (name, price, duration, description, image_path) VALUES (?, ?, ?, ?, ?)',
                    (request.form['serviceName'],
                     request.form['servicePrice'],
                     request.form['serviceDuration'],
                     request.form['serviceDescription'],
                     'uploads/services/' + filename))
        conn.commit()
        conn.close()
        
        flash('Service uploaded successfully!')
        return jsonify({'success': True})
    
    flash('Invalid file type')
    return jsonify({'success': False})

# Routes for displaying products and services
@app.route('/products')
def products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/services')
def services():
    conn = get_db_connection()
    services = conn.execute('SELECT * FROM services ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('services.html', services=services)

@app.route('/')
def index():
    return render_template('index_landing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def us_login():
    return render_template('user_login.html')

@app.route('/signup')
def us_signup():
    return render_template('user_signup.html')

# Cart functionality
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

@app.route('/book-service/<int:service_id>', methods=['POST'])
def book_service(service_id):
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Please login to book a service'})
    
    conn = get_db_connection()
    service = conn.execute('SELECT * FROM services WHERE id = ?', (service_id,)).fetchone()
    
    if service:
        # Add booking to bookings table
        conn.execute('''
            INSERT INTO bookings (user_id, service_id, booking_date, status)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], service_id, datetime.now(), 'pending'))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Service booked successfully'})
    
    conn.close()
    return jsonify({'success': False, 'message': 'Service not found'})

@app.route('/view-cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

if __name__ == '__main__':
    app.run(debug=True) 