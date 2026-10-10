from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
from botocore.exceptions import NoCredentialsError
from urllib.parse import unquote
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()  # reads settings from a local .env file (never committed)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-change-me')

# Settings come from environment variables — see .env.example
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
REGION = os.environ.get('AWS_REGION', 'ap-southeast-1')

s3 = boto3.client(
    's3',
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

USERS_FILE = 'users.json'

# ── Helper: load/save users ──────────────────────────────
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# ── Login required decorator ─────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── Routes ───────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        users = load_users()
        if username in users:
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        users[username] = generate_password_hash(password)
        save_users(users)
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        users = load_users()
        if username not in users or not check_password_hash(users[username], password):
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    try:
        username = session['username']
        files = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"{username}/")
        file_list = []
        if 'Contents' in files:
            for file in files['Contents']:
                file_list.append({
                    'name': file['Key'].replace(f"{username}/", ""),
                    'key': file['Key'],
                    'url': s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': BUCKET_NAME, 'Key': file['Key']},
                        ExpiresIn=3600
                    )
                })
    except Exception as e:
        file_list = []
        print(f"Error: {e}")
    return render_template('index.html', files=file_list, username=session['username'])

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    if file:
        try:
            s3.upload_fileobj(file, BUCKET_NAME, f"{session['username']}/{file.filename}")
        except NoCredentialsError:
            return "Credentials not available", 403
    return redirect(url_for('index'))

@app.route('/delete/<path:filename>', methods=['POST'])
@login_required
def delete(filename):
    try:
        filename = unquote(filename)
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
    except Exception as e:
        print(f"Error deleting file: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)