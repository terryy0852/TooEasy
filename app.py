# Flask Application for Educational Platform
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
import logging
import sys
from sqlalchemy import text

# Set up logging (early to capture all errors)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure from environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-in-production')

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Database configuration
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')

# Handle PostgreSQL URL conversion for SQLAlchemy compatibility
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    logger.info(f"Using DATABASE_URL from environment: {DATABASE_URL[:20]}...")
    # Fix Railway PostgreSQL URL format
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        logger.info(f"Converted to SQLAlchemy format: {DATABASE_URL[:20]}...")
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    sqlite_path = f'sqlite:///{os.path.join(instance_dir, "assignments.db")}'
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_path
    logger.info(f"Using SQLite database: {sqlite_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = False  # Always False in production

# Babel configuration
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

# Association table for student assignments
student_assignment = db.Table('student_assignment',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('assignment_id', db.Integer, db.ForeignKey('assignment.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)

# Assignment model
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to students (many-to-many)
    assigned_students = db.relationship('User', secondary=student_assignment, backref='assigned_assignments', lazy='dynamic')

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
login_manager.login_message = 'Please log in to access this page.'
login_manager.session_protection = 'strong'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {e}")
        return None

# Babel locale selector
def get_locale():
    try:
        if 'language' in session:
            return session['language']
        return request.accept_languages.best_match(['zh_CN', 'en', 'zh_TW']) or 'en'
    except Exception as e:
        logger.error(f"Error in locale selector: {e}")
        return 'en'

babel.init_app(app, locale_selector=get_locale)

# Health check endpoint for Railway
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0'
    }), 200

# Database initialization function
def init_database():
    with app.app_context():
        try:
            logger.info("Initializing database...")
            # Test connection first using text() for raw SQL
            db.session.execute(text('SELECT 1'))
            logger.info("Database connection successful")
            
            # Create tables if they don't exist
            db.create_all()
            logger.info("Database tables initialized successfully")
            
            # Create admin user if it doesn't exist
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                logger.info("Creating admin user...")
                admin_user = User(username='admin', email='admin@example.com', role='admin')
                admin_user.set_password('admin123')  # Use a secure password in production
                db.session.add(admin_user)
                db.session.commit()
                logger.info("Admin user created successfully")
            
            logger.info("Database initialization complete")
            return True
            
        except Exception as e:
            logger.critical(f"Failed to initialize database: {e}")
            logger.exception("Detailed error:")
            return False

# Routes and application logic
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
            login_user(user, remember=True)
            flash(_('Login successful!'))
            # Redirect based on user role
            if user.role == 'admin' or user.role == 'teacher':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash(_('Invalid username or password'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'))
    return redirect(url_for('login'))

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
        # Get assignments assigned to this student
        assignments = Assignment.query.join(
            student_assignment, 
            Assignment.id == student_assignment.c.assignment_id
        ).filter(
            student_assignment.c.student_id == current_user.id,
            Assignment.is_active == True
        ).all()
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
    
    # Get all students for the dropdown
    students = User.query.filter_by(role='student').all()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date_str = request.form.get('due_date')
        is_active = 'is_active' in request.form
        
        # Get selected student IDs
        selected_student_ids = request.form.getlist('student_ids')
        
        # Parse due date if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash(_('Invalid due date format'))
                return render_template('create_assignment.html', students=students)
        
        new_assignment = Assignment(
            title=title,
            description=description,
            created_by=current_user.id,
            due_date=due_date,
            is_active=is_active
        )
        
        try:
            db.session.add(new_assignment)
            db.session.flush()  # Get the assignment ID
            
            # Assign to selected students
            if selected_student_ids:
                for student_id in selected_student_ids:
                    student = User.query.get(int(student_id))
                    if student and student.role == 'student':
                        new_assignment.assigned_students.append(student)
            else:
                # If no students selected, assign to all students
                for student in students:
                    new_assignment.assigned_students.append(student)
            
            db.session.commit()
            flash(_('Assignment created successfully'))
            return redirect(url_for('student_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(_('Failed to create assignment'))
            print(f"Error creating assignment: {e}")
    
    return render_template('create_assignment.html', students=students)

@app.route('/view_assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Check if student has access to this assignment
    if current_user.role == 'student':
        # Check if assignment is assigned to this student
        assignment_assigned = db.session.query(student_assignment).filter(
            student_assignment.c.assignment_id == assignment_id,
            student_assignment.c.student_id == current_user.id
        ).first()
        
        if not assignment_assigned:
            flash(_('Access denied - this assignment is not assigned to you'))
            return redirect(url_for('student_dashboard'))
    
    return render_template('view_assignment.html', assignment=assignment)

@app.route('/submit_assignment/<int:assignment_id>', methods=['POST'])
@login_required
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

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if current_user.role != 'admin':
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Update user information
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']
        
        # Update password if provided
        if request.form['password']:
            user.set_password(request.form['password'])
        
        try:
            db.session.commit()
            flash(_('User updated successfully'))
            return redirect(url_for('admin_users'))
        except:
            flash(_('Failed to update user'))
    
    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting current user
    if user.id == current_user.id:
        flash(_('Cannot delete your own account'))
        return redirect(url_for('admin_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(_('User deleted successfully'))
    except:
        flash(_('Failed to delete user'))
    
    return redirect(url_for('admin_users'))

# Initialize the database
@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Internal Server Error: {error}")
    logger.exception("Error details:")
    return render_template('error.html', error="Internal Server Error"), 500

@app.errorhandler(Exception)
def unhandled_exception(error):
    logger.error(f"Unhandled Exception: {error}")
    logger.exception("Exception details:")
    return render_template('error.html', error="Server Error"), 500

# Start the application
if __name__ == '__main__':
    logger.info("Starting application...")
    logger.info(f"Environment: DATABASE_URL={'Configured' if DATABASE_URL else 'SQLite'}")
    
    # Initialize database
    if init_database():
        logger.info("Application starting successfully")
        port = int(os.environ.get('PORT', 5000))
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        logger.critical("Application failed to start due to database initialization error")
        sys.exit(1)