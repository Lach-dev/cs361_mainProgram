from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory user storage
users = {}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/information')
def information():
    return render_template('information.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists.')
        else:
            users[username] = generate_password_hash(password)
            flash('Registration successful.')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and check_password_hash(user, password):
            session['username'] = username
            flash('Login successful.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    return f'Welcome, {session["username"]}! This is the dashboard.'


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
