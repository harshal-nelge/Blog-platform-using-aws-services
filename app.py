from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from models import DynamoDBManager, S3Manager, CognitoManager

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize AWS services
db_manager = DynamoDBManager()
s3_manager = S3Manager()
cognito_manager = CognitoManager()

# Helper function to check if user is logged in
def is_logged_in():
    return 'username' in session

@app.route('/')
def index():
    posts = db_manager.get_all_posts()
    return render_template('index.html', posts=posts, logged_in=is_logged_in())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        success, result = cognito_manager.register_user(username, email, password)
        
        if success:
            flash('Registration successful! Please check your email for confirmation code.')
            return redirect(url_for('confirm_registration', username=username))
        else:
            flash(f'Registration failed: {result}')
    
    return render_template('register.html', logged_in=is_logged_in())

@app.route('/confirm/<username>', methods=['GET', 'POST'])
def confirm_registration(username):
    if request.method == 'POST':
        confirmation_code = request.form['confirmation_code']
        success, result = cognito_manager.confirm_user(username, confirmation_code)
        
        if success:
            flash('Email confirmed! You can now login.')
            return redirect(url_for('login'))
        else:
            flash(f'Confirmation failed: {result}')
    
    return render_template('confirm.html', username=username, logged_in=is_logged_in())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        success, result = cognito_manager.login_user(username, password)
        
        if success:
            session['username'] = username
            # Typically you'd store tokens in session but for simplicity we're just storing username
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash(f'Login failed: {result}')
    
    return render_template('login.html', logged_in=is_logged_in())

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if not is_logged_in():
        flash('Please login to create a post.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = session['username']
        image_url = None
        
        # Handle image upload
        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            filename = secure_filename(image.filename)
            image_url = s3_manager.upload_image(image, filename)
        
        # Create the post in DynamoDB
        post_id = db_manager.create_post(title, content, author, image_url)
        
        flash('Post created successfully!')
        return redirect(url_for('view_post', post_id=post_id))
    
    return render_template('create_post.html', logged_in=is_logged_in())

@app.route('/post/<post_id>')
def view_post(post_id):
    post = db_manager.get_post(post_id)
    if not post:
        flash('Post not found.')
        return redirect(url_for('index'))
    
    return render_template('post.html', post=post, logged_in=is_logged_in())

if __name__ == '__main__':
    app.run(debug=True)