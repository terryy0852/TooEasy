# Standalone Flask app to test password reset functionality
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_password_reset.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model with password reset fields
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    reset_token = db.Column(db.String(64), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()
    # Add a test user
    if not User.query.filter_by(username='testuser').first():
        test_user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('Test123!')
        )
        db.session.add(test_user)
        db.session.commit()
        print("Test user created: username='testuser', password='Test123!'")

@app.route('/')
@login_required
def index():
    return f"Hello, {current_user.username}! <a href='{url_for('logout')}'>Logout</a>"

@app.route('/login', methods=['GET', 'POST'])  # 添加路由
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    # 添加基础模板
    base_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{% block title %}Password Reset System{% endblock %}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ccc;
            }
            .flash {
                color: red;
                margin: 10px 0;
            }
            input, button {
                display: block;
                width: 100%;
                margin: 10px 0;
                padding: 8px;
            }
            /* Browser dark mode override */
            @media (prefers-color-scheme: dark) {
                /* Reset all elements to light mode */
                :root {
                    --bg-color: #ffffff;
                    --text-color: #333333;
                    --card-bg: #ffffff;
                    --border-color: #ccc;
                }
                
                * {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border-color: var(--border-color) !important;
                }
                
                body {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border: 1px solid var(--border-color) !important;
                }
                
                .flash {
                    color: red !important;
                }
                
                input, button {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border: 1px solid var(--border-color) !important;
                }
                
                /* Ensure form elements don't inherit unwanted styles */
                input::placeholder {
                    color: #999 !important;
                }
            }
        </style>
    </head>
    <body>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="flash">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </body>
    </html>
    '''
    # 添加登录模板
    login_template = base_template.replace('{% block content %}{% endblock %}', '''
    {% block content %}
        <h1>Login</h1>
        <form action="{{ url_for('login') }}" method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div style="margin-top: 15px; text-align: center;">
            <a href="/forgot_password">Forgot Password?</a>
        </div>
    {% endblock %}
    ''')
    return render_template_string(login_template)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate reset token
            user.reset_token = str(uuid.uuid4())
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # In a real app, send this token via email
            flash(f"Password reset token generated: {user.reset_token}")
        else:
            flash('If an account with that email exists, a reset token will be sent')
    
    # Load base template with dark mode override
    base_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{% block title %}Password Reset System{% endblock %}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 50px auto;
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            .flash {
                color: red;
                margin: 10px 0;
            }
            input, button {
                display: block;
                width: 100%;
                margin: 10px 0;
                padding: 10px;
            }
            /* Browser dark mode override */
            @media (prefers-color-scheme: dark) {
                /* Reset all elements to light mode */
                :root {
                    --bg-color: #ffffff;
                    --text-color: #333333;
                    --card-bg: #ffffff;
                    --border-color: #ccc;
                }
                
                * {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border-color: var(--border-color) !important;
                }
                
                body {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border: 1px solid var(--border-color) !important;
                }
                
                .flash {
                    color: red !important;
                }
                
                input, button {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border: 1px solid var(--border-color) !important;
                }
                
                /* Ensure form elements don't inherit unwanted styles */
                input::placeholder {
                    color: #999 !important;
                }
            }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        {% for message in get_flashed_messages() %}
            <div class="flash">{{ message }}</div>
        {% endfor %}
        {% block content %}{% endblock %}
    </body>
    </html>
    '''
    
    # Forgot password form template
    forgot_template = '''
    {% block content %}
    <form method="post">
        <input type="email" name="email" placeholder="Email" required><br>
        <button type="submit">Request Reset Token</button>
    </form>
    <p><a href="{{ url_for('login') }}">Back to Login</a></p>
    {% endblock %}
    '''
    
    # Combine templates
    full_template = base_template.replace('{% block content %}{% endblock %}', forgot_template)
    return render_template_string(full_template, title='Forgot Password')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset token')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters long')
        else:
            user.password = generate_password_hash(new_password)
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            flash('Password has been reset successfully')
            return redirect(url_for('login'))
    
    # Load base template with dark mode override
    base_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{% block title %}Password Reset System{% endblock %}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 50px auto;
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            .flash {
                color: red;
                margin: 10px 0;
            }
            input, button {
                display: block;
                width: 100%;
                margin: 10px 0;
                padding: 10px;
            }
            /* Browser dark mode override */
            @media (prefers-color-scheme: dark) {
                /* Reset all elements to light mode */
                :root {
                    --bg-color: #ffffff;
                    --text-color: #333333;
                    --card-bg: #ffffff;
                    --border-color: #ccc;
                }
                
                * {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border-color: var(--border-color) !important;
                }
                
                body {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border: 1px solid var(--border-color) !important;
                }
                
                .flash {
                    color: red !important;
                }
                
                input, button {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border: 1px solid var(--border-color) !important;
                }
                
                /* Ensure form elements don't inherit unwanted styles */
                input::placeholder {
                    color: #999 !important;
                }
            }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        {% for message in get_flashed_messages() %}
            <div class="flash">{{ message }}</div>
        {% endfor %}
        {% block content %}{% endblock %}
    </body>
    </html>
    '''
    
    # Reset password form template
    reset_template = '''
    {% block content %}
    <form method="post">
        <input type="password" name="password" placeholder="New Password" required><br>
        <input type="password" name="confirm_password" placeholder="Confirm Password" required><br>
        <button type="submit">Reset Password</button>
    </form>
    <p><a href="{{ url_for('login') }}">Back to Login</a></p>
    {% endblock %}
    '''
    
    # Combine templates
    full_template = base_template.replace('{% block content %}{% endblock %}', reset_template)
    return render_template_string(full_template, title='Reset Password')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("Starting standalone password reset app on http://127.0.0.1:5001")
    print("Test user: username='testuser', password='Test123!'")
    app.run(debug=True, port=5001)



