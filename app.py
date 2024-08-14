import base64
import os
from io import BytesIO

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, send_file, \
    abort

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Base URL for the auth microservice
AUTH_URL = "http://auth-microservice:8000"

ENCDEC_URL = "http://encdec-microservice:8001"


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

        # Send registration data to the microservice
        response = requests.post(f"{AUTH_URL}/register", json={"username": username, "password": password})

        # Check if the response was successful
        if response.status_code == 201:  # HTTP 201 Created
            try:
                response_json = response.json()
                flash(response_json.get('message', 'Registration successful!'), 'success')
            except requests.exceptions.JSONDecodeError:
                flash('Registration successful, but failed to decode JSON response.', 'warning')
            return redirect(url_for('login'))  # Redirect to the login page
        elif response.status_code == 400:  # HTTP 400 Bad Request (e.g., username already exists)
            try:
                response_json = response.json()
                flash(response_json.get('detail', 'Failed to register: Bad request.'), 'danger')
            except requests.exceptions.JSONDecodeError:
                flash('Failed to register and failed to decode JSON response.', 'danger')
        else:
            # Handle other unexpected status codes
            flash(f"Failed to register: Unexpected status code {response.status_code}.", 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Send login data to the microservice
        response = requests.post(f"{AUTH_URL}/login", json={"username": username, "password": password})

        if response.status_code == 200:
            session['username'] = username
            flash('Login successful.')
            return redirect(url_for('upload'))
        else:
            flash(response.json().get('detail', 'Invalid username or password.'))

    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            # Read the file content as bytes
            file_bytes = file.read()

            # Base64 encode the file content
            encoded_data = base64.b64encode(file_bytes)

            # Send the encoded data to the encryption service
            response = requests.post(f"{ENCDEC_URL}/encrypt", data=encoded_data)

            if response.status_code == 200:
                encrypted_data = response.json()["encrypted_data"]

                # Save the encrypted data as a file
                encrypted_filename = file.filename + ".enc"
                encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
                with open(encrypted_path, 'w') as f:
                    f.write(encrypted_data)

                flash(f'File {file.filename} encrypted and uploaded successfully')
                uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
                return render_template('upload.html', files=uploaded_files)
            else:
                flash('Failed to encrypt the file.')
                return redirect(request.url)

    return render_template('upload.html')


@app.route('/download/<filename>')
def download_file(filename):
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(encrypted_path):
        abort(404)

    # Read the encrypted data from the file
    with open(encrypted_path, 'r') as f:
        encrypted_data = f.read()

    # Send the encrypted data to the decryption service
    response = requests.post(f"{ENCDEC_URL}/decrypt", json={"encrypted_data": encrypted_data})

    if response.status_code == 200:
        decrypted_data = response.json()["decrypted_data"]

        # Decode the base64 data back to bytes
        file_bytes = base64.b64decode(decrypted_data)

        # Return the decrypted file to the user
        return send_file(BytesIO(file_bytes), as_attachment=True, download_name=filename.replace(".enc", ""))

    else:
        flash('Failed to decrypt the file.')
        return redirect(url_for('view_files'))


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


@app.route('/download')
def view_download():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('download.html', files=files)


if __name__ == '__main__':
    app.run(debug=True)
