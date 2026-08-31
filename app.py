# MINIMAL BULLETPROOF VERSION - Login page renders without any DB/Babel complexity
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import sys
import logging

# Ultra-simple logging - stdout only, never fails
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Session config
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# CSRF (needed for forms but won't crash if broken)
try:
    csrf = CSRFProtect(app)
except Exception as e:
    logger.warning(f"CSRF init warning (non-fatal): {e}")

# Uploads directory - simple, with fallback to /tmp
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception:
    import tempfile
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database config - USE POSTGRES if DATABASE_URL exists, else SQLite fallback
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Convert to psycopg v3 format
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
    elif DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    logger.info("Using PostgreSQL database")
else:
    # SQLite fallback
    instance_dir = os.path.join(BASE_DIR, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    sqlite_path = f'sqlite:///{os.path.join(instance_dir, "assignments.db")}'
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_path
    logger.info("Using SQLite database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    student_ids = db.Column(db.Text)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    teacher = db.relationship('User', backref='assignments', lazy=True)

class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(500))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assignment = db.relationship('Assignment', backref='submissions', lazy=True)
    student = db.relationship('User', backref='submissions', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database initialization
_db_initialized = False

def init_database():
    global _db_initialized
    if _db_initialized:
        return True
    try:
        logger.info("Initializing database...")
        db.create_all()
        
        # Create admin user if doesn't exist
        try:
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                logger.info("Creating admin user...")
                admin = User(username='admin', email='admin@example.com', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created")
        except Exception as admin_err:
            logger.warning(f"Admin creation warning: {admin_err}")
            db.session.rollback()
        
        _db_initialized = True
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "version": "1.0"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Only initialize DB when user actually tries to login
        init_database()
        
        try:
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
                session.permanent = True
                flash('Login successful!')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid username or password')
        except Exception as login_err:
            logger.error(f"Login error: {login_err}")
            flash('Login error. Please try again.')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        init_database()
        
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form.get('role', 'student')
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))
            
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as reg_err:
            db.session.rollback()
            logger.error(f"Registration error: {reg_err}")
            flash('Registration failed. Please try again.')
    
    return render_template('register.html')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    init_database()
    
    try:
        if current_user.role == 'student':
            # Get assignments assigned to this student
            all_assignments = Assignment.query.all()
            student_assignments = []
            
            for assignment in all_assignments:
                if assignment.student_ids:
                    student_id_list = [int(id.strip()) for id in assignment.student_ids.split(',') if id.strip()]
                    if current_user.id in student_id_list:
                        student_assignments.append(assignment)
            
            # Get submissions for this student
            submissions = Submission.query.filter_by(student_id=current_user.id).all()
            
            return render_template('student_dashboard.html', 
                                 assignments=student_assignments,
                                 submissions=submissions)
        
        elif current_user.role == 'teacher' or current_user.role == 'admin':
            # Get all students
            students = User.query.filter_by(role='student').all()
            
            # Get all assignments created by this teacher
            assignments = Assignment.query.filter_by(assigned_by=current_user.id).all()
            
            # Get all submissions
            submissions = Submission.query.all()
            
            return render_template('teacher_dashboard.html',
                                 students=students,
                                 assignments=assignments,
                                 submissions=submissions)
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash('Error loading dashboard')
        return redirect(url_for('login'))

# Create assignment route (teachers only)
@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if current_user.role not in ['teacher', 'admin']:
        flash('Permission denied')
        return redirect(url_for('student_dashboard'))
    
    init_database()
    
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            student_ids = request.form.getlist('students')  # List of selected student IDs
            html_file = request.files.get('html_file')
            
            # Save uploaded file if provided
            file_path = None
            if html_file and html_file.filename:
                filename = f"assignment_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{html_file.filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                html_file.save(file_path)
            
            # Create assignment
            assignment = Assignment(
                title=title,
                description=description,
                file_path=file_path,
                student_ids=','.join(student_ids),
                assigned_by=current_user.id
            )
            
            db.session.add(assignment)
            db.session.commit()
            
            flash('Assignment created successfully!')
            return redirect(url_for('student_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Assignment creation error: {e}")
            flash('Error creating assignment')
    
    # GET request - show form
    try:
        students = User.query.filter_by(role='student').all()
        return render_template('create_assignment.html', students=students)
    except Exception as e:
        logger.error(f"Create assignment form error: {e}")
        flash('Error loading form')
        return redirect(url_for('student_dashboard'))

# Submit assignment route (students only)
@app.route('/submit_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    if current_user.role != 'student':
        flash('Permission denied')
        return redirect(url_for('student_dashboard'))
    
    init_database()
    
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check if student is assigned to this assignment
        if assignment.student_ids:
            student_id_list = [int(id.strip()) for id in assignment.student_ids.split(',') if id.strip()]
            if current_user.id not in student_id_list:
                flash('You are not assigned to this assignment')
                return redirect(url_for('student_dashboard'))
        
        if request.method == 'POST':
            html_file = request.files.get('html_submission')
            
            if html_file and html_file.filename:
                # Save submitted file
                filename = f"submission_{current_user.id}_{assignment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{html_file.filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                html_file.save(file_path)
                
                # Create or update submission record
                existing_submission = Submission.query.filter_by(
                    assignment_id=assignment_id,
                    student_id=current_user.id
                ).first()
                
                if existing_submission:
                    existing_submission.file_path = file_path
                    existing_submission.submitted_at = datetime.utcnow()
                else:
                    submission = Submission(
                        assignment_id=assignment_id,
                        student_id=current_user.id,
                        file_path=file_path
                    )
                    db.session.add(submission)
                
                db.session.commit()
                flash('Assignment submitted successfully!')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Please upload an HTML file')
        
        return render_template('submit_assignment.html', assignment=assignment)
        
    except Exception as e:
        logger.error(f"Assignment submission error: {e}")
        flash('Error processing submission')
        return redirect(url_for('student_dashboard'))

# View submission route (teachers only)
@app.route('/view_submission/<int:submission_id>')
@login_required
def view_submission(submission_id):
    if current_user.role not in ['teacher', 'admin']:
        flash('Permission denied')
        return redirect(url_for('student_dashboard'))
    
    init_database()
    
    try:
        submission = Submission.query.get_or_404(submission_id)
        assignment = Assignment.query.get(submission.assignment_id)
        student = User.query.get(submission.student_id)
        
        # Read and display the submitted HTML file
        html_content = ""
        if submission.file_path and os.path.exists(submission.file_path):
            try:
                with open(submission.file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except Exception as e:
                logger.error(f"Error reading submission file: {e}")
                html_content = "Error reading submission file"
        
        return render_template('view_submission.html',
                             submission=submission,
                             assignment=assignment,
                             student=student,
                             html_content=html_content)
    
    except Exception as e:
        logger.error(f"View submission error: {e}")
        flash('Error viewing submission')
        return redirect(url_for('student_dashboard'))

# Delete assignment route (teachers only)
@app.route('/delete_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    if current_user.role not in ['teacher', 'admin']:
        flash('Permission denied')
        return redirect(url_for('student_dashboard'))
    
    init_database()
    
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Delete associated submissions
        submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
        for submission in submissions:
            if submission.file_path and os.path.exists(submission.file_path):
                try:
                    os.remove(submission.file_path)
                except Exception as e:
                    logger.error(f"Error deleting submission file: {e}")
            db.session.delete(submission)
        
        # Delete assignment file if it exists
        if assignment.file_path and os.path.exists(assignment.file_path):
            try:
                os.remove(assignment.file_path)
            except Exception as e:
                logger.error(f"Error deleting assignment file: {e}")
        
        db.session.delete(assignment)
        db.session.commit()
        
        flash('Assignment deleted successfully!')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete assignment error: {e}")
        flash('Error deleting assignment')
    
    return redirect(url_for('student_dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Context processors
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
