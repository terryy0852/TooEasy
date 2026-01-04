# Flask Application for Educational Platform
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

# Initialize Flask app
app = Flask(__name__)

# Use environment variables for configuration
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-in-production')

# Database configuration - use PostgreSQL from Railway environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set to False in production
app.config['DEBUG'] = False

# Babel configuration for translations
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'

# Initialize database
db = SQLAlchemy(app)

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Assignment model
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

# Submission model
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Babel locale selector
def get_locale():
    # Try to get locale from session
    if 'language' in session:
        return session['language']
    # Fall back to browser's preferred language
    return request.accept_languages.best_match(['zh_CN', 'en', 'zh_TW']) or 'en'

babel.init_app(app, locale_selector=get_locale)

# Add health check endpoint for Railway
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # Redirect based on user role
            if user.role == 'admin' or user.role == 'teacher':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash(_('Invalid username or password'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'student')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash(_('Username already exists'))
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash(_('Email already registered'))
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(_('Registration successful! Please login.'))
            return redirect(url_for('login'))
        except:
            flash(_('Registration failed. Please try again.'))
    
    return render_template('register.html')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role == 'student':
        # Get assignments for student
        assignments = Assignment.query.filter_by(is_active=True).all()
        return render_template('student_dashboard.html', assignments=assignments)
    else:
        # For teachers/admin, show all assignments and submissions
        assignments = Assignment.query.all()
        return render_template('student_dashboard.html', assignments=assignments)

@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        new_assignment = Assignment(
            title=title,
            description=description,
            created_by=current_user.id
        )
        
        try:
            db.session.add(new_assignment)
            db.session.commit()
            flash(_('Assignment created successfully'))
            return redirect(url_for('student_dashboard'))
        except:
            flash(_('Failed to create assignment'))
    
    return render_template('create_assignment.html')

@app.route('/view_assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    return render_template('view_assignment.html', assignment=assignment)

@app.route('/submit_assignment/<int:assignment_id>', methods=['POST'])
def submit_assignment(assignment_id):
    if request.method == 'POST':
        content = request.form['content']
        
        new_submission = Submission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            content=content
        )
        
        try:
            db.session.add(new_submission)
            db.session.commit()
            
            # Generate HTML file for submission
            try:
                # Define the HTML template
                html_doc = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Submission</title>
    <style>
        /* Browser dark mode override */
        :root {
            --background-color: #ffffff !important;
            --text-color: #000000 !important;
            --code-background: #f5f5f5 !important;
            --code-text: #000000 !important;
        }
        
        * {
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
        }
        
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        
        pre {
            background-color: var(--code-background) !important;
            color: var(--code-text) !important;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>Student Submission</h1>
    <p><strong>Assignment ID:</strong> {assignment_id}</p>
    <p><strong>Student ID:</strong> {current_user.id}</p>
    <p><strong>Submitted at:</strong> {new_submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <h2>Content:</h2>
    <pre>{content}</pre>
</body>
</html>
"""
                
                # Save the HTML file
                filename = f"submission_{assignment_id}_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_doc)
                    print(f"Saved submission as {filename}")
                    
            except Exception as e:
                print(f"Error saving HTML: {e}")
            
            return render_template('assignment_submitted.html', assignment_id=assignment_id)
        except Exception as e:
            flash(_('Failed to submit assignment'))
            print(f"Error submitting assignment: {e}")
            return redirect(url_for('view_assignment', assignment_id=assignment_id))

@app.route('/view_submissions/<int:assignment_id>')
@login_required
def view_submissions(assignment_id):
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    return render_template('view_submissions.html', submissions=submissions, assignment_id=assignment_id)

@app.route('/grade_submission/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def grade_submission(submission_id):
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    
    submission = Submission.query.get_or_404(submission_id)
    
    if request.method == 'POST':
        grade = request.form['grade']
        feedback = request.form['feedback']
        
        submission.grade = float(grade)
        submission.feedback = feedback
        
        try:
            db.session.commit()
            flash(_('Submission graded successfully'))
            return redirect(url_for('view_submissions', assignment_id=submission.assignment_id))
        except:
            flash(_('Failed to grade submission'))
    
    return render_template('grade_submission.html', submission=submission)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # In a real app, send a reset email
            flash(_('Password reset instructions sent to your email'))
        else:
            flash(_('Email not found'))
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        password = request.form['password']
        # In a real app, verify the token and update password
        flash(_('Password reset successfully'))
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        
        if current_user.check_password(current_password):
            current_user.set_password(new_password)
            db.session.commit()
            flash(_('Password changed successfully'))
            return redirect(url_for('student_dashboard'))
        else:
            flash(_('Current password is incorrect'))
    return render_template('change_password.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Initialize the database
def create_tables():
    with app.app_context():
        db.create_all()
        print("[DB INIT] All tables already exist")

# Start the application
if __name__ == '__main__':
    create_tables()
    # Run without debug mode to prevent auto-restarting
    app.run(debug=False, host='0.0.0.0', port=5000)

