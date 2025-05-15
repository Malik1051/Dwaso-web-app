from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True) 