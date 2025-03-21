from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)


# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Use port 5000 for development