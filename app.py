import os

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# ong ill do this later
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
            return redirect(url_for('upload'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # if 'username' not in session:
    #     flash('You need to log in first.')
    #     return redirect(url_for('login'))
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file:
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload'))
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=uploaded_files)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/view')
def view_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('view.html', files=files)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('view_files'))


@app.route('/delete')
def view_delete():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('delete.html', files=files)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/download')
def view_download():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('download.html', files=files)


if __name__ == '__main__':
    app.run(debug=True)
