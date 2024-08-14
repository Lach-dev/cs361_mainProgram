import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = '/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Base URL for the FastAPI microservice
MICROSERVICE_URL = "http://localhost:8000"


@app.route('/')
def home():
    return render_template('C:\\Users\11thu\\PycharmProjects\\mainProgram_cs361\\mainApp\\templates\\home.html')


@app.route('/information')
def information():
    return render_template('/templates/information.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Send registration data to the microservice
        response = requests.post(f"{MICROSERVICE_URL}/register", json={"username": username, "password": password})

        if response.status_code == 201:
            flash('Registration successful.')
            return redirect(url_for('login'))
        else:
            flash(response.json().get('detail', 'Registration failed.'))

    return render_template('/templates/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Send login data to the microservice
        response = requests.post(f"{MICROSERVICE_URL}/login", json={"username": username, "password": password})

        if response.status_code == 200:
            session['username'] = username
            flash('Login successful.')
            return redirect(url_for('upload'))
        else:
            flash(response.json().get('detail', 'Invalid username or password.'))

    return render_template('/templates/login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file:
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload'))
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('/templates/upload.html', files=uploaded_files)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/view')
def view_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('/templates/view.html', files=files)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('view_files'))


@app.route('/delete')
def view_delete():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('/templates/delete.html', files=files)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/download')
def view_download():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('/templates/download.html', files=files)


if __name__ == '__main__':
    app.run(debug=True)
