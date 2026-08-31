# Flask Application for Educational Platform
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext as _
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
import logging
import sys
from sqlalchemy import text

# ──────────────────────────────────────────────────────────────
# FIX 1: Logging — stdout ONLY (no file writes on Railway!)
# Railway filesystem is read-only except under /app
# File logging causes Gunicorn workers to crash at startup
# ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# FIX 2: Writable paths — use env UPLOAD_FOLDER, default /app/uploads
# Railway requires writable dirs to be under /app (not root /uploads)
# ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(BASE_DIR, 'uploads')

# ──────────────────────────────────────────────────────────────
# Initialize Flask app
# ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me-2026')
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Session
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Uploads
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Ensure uploads dir exists (safe, idempotent)
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    logger.info(f"UPLOAD_FOLDER: {UPLOAD_FOLDER} (created/verified)")
except Exception as e:
    logger.warning(f"Could not create UPLOAD_FOLDER {UPLOAD_FOLDER}: {e}")

# CSRF
csrf = CSRFProtect(app)

# ──────────────────────────────────────────────────────────────
# FIX 3: Babel initialized ONCE, with locale_selector at init
# Previous code init'd Babel 3 times (lines 53, 78, 163) causing issues
# ──────────────────────────────────────────────────────────────
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(BASE_DIR, 'translations')

def get_locale():
    try:
        if 'language' in session:
            return session['language']
        return request.accept_languages.best_match(['zh_CN', 'en', 'zh_TW']) or 'en'
    except Exception:
        return 'en'

babel = Babel(app, locale_selector=get_locale)

# ──────────────────────────────────────────────────────────────
# FIX 4: Database — lazy init via SQLAlchemy(app) but NO module-level queries
# init_database() called via before_request (lazy) — NOT in __main__ only
# Railway Gunicorn spawns workers that import app, __main__ never runs!
# ──────────────────────────────────────────────────────────────
instance_dir = os.path.join(BASE_DIR, 'instance')
try:
    os.makedirs(instance_dir, exist_ok=True)
except Exception:
    pass

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Fix Railway PostgreSQL URL format (postgres:// -> postgresql://)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    logger.info(f"Using PostgreSQL DATABASE_URL: {DATABASE_URL[:30]}...")
else:
    sqlite_path = f'sqlite:///{os.path.join(instance_dir, "assignments.db")}'
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_path
    logger.info(f"Using SQLite: {sqlite_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)

# ──────────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    __tablename__ = 'user'
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


student_assignment = db.Table(
    'student_assignment',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('assignment_id', db.Integer, db.ForeignKey('assignment.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)


class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    html_filename = db.Column(db.String(255), nullable=True)
    html_content = db.Column(db.Text, nullable=True)

    assigned_students = db.relationship(
        'User',
        secondary=student_assignment,
        backref='assigned_assignments',
        lazy='dynamic'
    )


class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    screenshot_filename = db.Column(db.String(255), nullable=True)

    assignment = db.relationship('Assignment', backref='submissions', lazy=True)
    user = db.relationship('User', backref='submissions', lazy=True)

# ──────────────────────────────────────────────────────────────
# FIX 5: Flask-Login
# ──────────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.session_protection = 'basic'  # relaxed from 'strong' for Railway proxy

@login_manager.user_loader
def load_user(user_id):
    try:
        with app.app_context():
            return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"load_user error: {e}")
        return None

# ──────────────────────────────────────────────────────────────
# FIX 6: Lazy database init — runs ONCE on first request, safe
# __main__ block never runs under Gunicorn, so we use before_request
# ──────────────────────────────────────────────────────────────
_db_initialized = False

def init_database():
    global _db_initialized
    if _db_initialized:
        return
    try:
        with app.app_context():
            # Test connection
            db.session.execute(text('SELECT 1'))
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            if not existing_tables:
                logger.info("Creating database tables...")
                db.create_all()
                logger.info("Tables created")
            else:
                logger.info(f"Tables exist: {existing_tables}")

            # Seed admin user if missing (safe)
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                try:
                    admin_user = User(
                        username='admin',
                        email='admin@example.com',
                        role='admin'
                    )
                    admin_user.set_password('admin123')
                    db.session.add(admin_user)
                    db.session.commit()
                    logger.info("Admin user seeded (change password!)")
                except Exception as e:
                    db.session.rollback()
                    logger.warning(f"Seed admin failed (may already exist): {e}")
        _db_initialized = True
        logger.info("Database initialization complete")
    except Exception as e:
        logger.critical(f"FAILED to init database: {e}", exc_info=True)

@app.before_request
def ensure_db_ready():
    init_database()

# ──────────────────────────────────────────────────────────────
# Health check (Railway)
# ──────────────────────────────────────────────────────────────
@app.route('/health')
def health_check():
    try:
        init_database()
        with app.app_context():
            db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'db': 'ok',
            'version': '1.1-fixed'
        }), 200
    except Exception as e:
        logger.error(f"Health check FAIL: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'version': '1.1-fixed'
        }), 500

# ──────────────────────────────────────────────────────────────
# Uploads
# ──────────────────────────────────────────────────────────────
@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"serve_uploaded_file error {filename}: {e}")
        return "File not found", 404

# ──────────────────────────────────────────────────────────────
# FIX 7: Error handlers — return proper (Response, code) tuples
# Old code: log_exception() registered as error handler returns None
# Returning None from an error handler = 500 with no response body
# ──────────────────────────────────────────────────────────────
@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"500 Internal Server Error: {error}", exc_info=True)
    return render_template('error.html', error="Internal Server Error"), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('error.html', error="Forbidden"), 403

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"UNHANDLED EXCEPTION: {type(error).__name__}: {error}", exc_info=True)
    return render_template('error.html', error=str(error)[:100]), 500

# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        init_database()
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            if not username or not password:
                flash(_('Username and password are required'))
                return render_template('login.html')

            with app.app_context():
                user = User.query.filter_by(username=username).first()
                if user and user.check_password(password):
                    login_user(user, remember=True)
                    session.permanent = True
                    flash(_('Login successful!'))
                    return redirect(url_for('student_dashboard'))
                else:
                    flash(_('Invalid username or password'))
    except Exception as e:
        logger.error(f"login route error: {e}", exc_info=True)
        flash(_('Login failed. Please try again.'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        init_database()
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role', 'student')

            if not username or not email or not password:
                flash(_('All fields are required'))
                return render_template('register.html')

            with app.app_context():
                if User.query.filter_by(username=username).first():
                    flash(_('Username already exists'))
                    return render_template('register.html')
                if User.query.filter_by(email=email).first():
                    flash(_('Email already registered'))
                    return render_template('register.html')

                new_user = User(username=username, email=email, role=role)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

            flash(_('Registration successful! Please login.'))
            return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"register route error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Registration failed. Please try again.'))
    return render_template('register.html')


@app.route('/student_dashboard')
@login_required
def student_dashboard():
    try:
        init_database()
        logger.debug(f"student_dashboard: {current_user.username} ({current_user.role})")
        with app.app_context():
            if current_user.role == 'student':
                assignments = Assignment.query.join(
                    student_assignment,
                    Assignment.id == student_assignment.c.assignment_id
                ).filter(
                    student_assignment.c.student_id == current_user.id,
                    Assignment.is_active == True
                ).all()
                assignment_submissions = {}
                for a in assignments:
                    sub = Submission.query.filter_by(
                        assignment_id=a.id, student_id=current_user.id
                    ).first()
                    assignment_submissions[a.id] = sub
                return render_template(
                    'student_dashboard.html',
                    assignments=assignments,
                    assignment_submissions=assignment_submissions
                )
            else:
                assignments = Assignment.query.all()
                return render_template('student_dashboard.html', assignments=assignments)
    except Exception as e:
        logger.error(f"student_dashboard error: {e}", exc_info=True)
        flash(_('Error loading dashboard'))
        return redirect(url_for('login'))


@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))

    try:
        init_database()
        with app.app_context():
            students = User.query.filter_by(role='student').all()

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            due_date_str = request.form.get('due_date')
            is_active = 'is_active' in request.form
            selected_student_ids = request.form.getlist('student_ids')
            html_file = request.files.get('html_file')

            if not title or not description:
                flash(_('Title and description are required'))
                return render_template('create_assignment.html', students=students)

            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass

            with app.app_context():
                new_assignment = Assignment(
                    title=title,
                    description=description,
                    created_by=current_user.id,
                    due_date=due_date,
                    is_active=is_active
                )
                db.session.add(new_assignment)
                db.session.flush()

                # HTML file handling
                if html_file and html_file.filename:
                    if html_file.filename.lower().endswith('.html'):
                        filename = f"assignment_{new_assignment.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.html"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        try:
                            html_file.save(filepath)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                new_assignment.html_content = f.read()
                            new_assignment.html_filename = filename
                        except Exception as e:
                            logger.error(f"HTML file save error: {e}")
                            flash(_('Could not save HTML file'))
                            db.session.rollback()
                            return render_template('create_assignment.html', students=students)
                    else:
                        flash(_('Only HTML files are allowed'))
                        return render_template('create_assignment.html', students=students)

                # Assign students
                if selected_student_ids:
                    for sid in selected_student_ids:
                        student = User.query.get(int(sid))
                        if student and student.role == 'student':
                            new_assignment.assigned_students.append(student)
                else:
                    for s in students:
                        new_assignment.assigned_students.append(s)

                db.session.commit()
            flash(_('Assignment created successfully'))
            return redirect(url_for('student_dashboard'))
    except Exception as e:
        logger.error(f"create_assignment error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to create assignment'))
        with app.app_context():
            students = User.query.filter_by(role='student').all()
    return render_template('create_assignment.html', students=students)


@app.route('/view_assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    try:
        init_database()
        with app.app_context():
            assignment = Assignment.query.get_or_404(assignment_id)

            if current_user.role == 'student':
                assigned = db.session.query(student_assignment).filter(
                    student_assignment.c.assignment_id == assignment_id,
                    student_assignment.c.student_id == current_user.id
                ).first()
                if not assigned:
                    flash(_('Access denied - this assignment is not assigned to you'))
                    return redirect(url_for('student_dashboard'))

            submission = None
            if current_user.role == 'student':
                submission = Submission.query.filter_by(
                    assignment_id=assignment_id,
                    student_id=current_user.id
                ).first()
        return render_template(
            'interactive_assignment.html',
            assignment=assignment,
            submission=submission
        )
    except Exception as e:
        logger.error(f"view_assignment {assignment_id} error: {e}", exc_info=True)
        flash(_('Error loading assignment'))
        return redirect(url_for('student_dashboard'))


@app.route('/submit_html_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def submit_html_assignment(assignment_id):
    if request.method != 'POST':
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    try:
        init_database()
        with app.app_context():
            assignment = Assignment.query.get_or_404(assignment_id)
            if current_user.role == 'student':
                assigned = db.session.query(student_assignment).filter(
                    student_assignment.c.assignment_id == assignment_id,
                    student_assignment.c.student_id == current_user.id
                ).first()
                if not assigned:
                    flash(_('Access denied'))
                    return redirect(url_for('student_dashboard'))

            existing = Submission.query.filter_by(
                assignment_id=assignment_id,
                student_id=current_user.id
            ).first()
            if existing:
                flash(_('You have already submitted this assignment'))
                return redirect(url_for('view_assignment', assignment_id=assignment_id))

            content = request.form.get('content', '').strip()
            if not content:
                flash(_('Please provide your HTML content'))
                return redirect(url_for('view_assignment', assignment_id=assignment_id))

            # Screenshot
            screenshot_filename = None
            if 'screenshot' in request.files:
                shot = request.files['screenshot']
                if shot and shot.filename:
                    ext = shot.filename.split('.')[-1].lower()
                    if ext in ('png', 'jpg', 'jpeg', 'gif'):
                        screenshot_filename = (
                            f"screenshot_{assignment_id}_{current_user.id}_"
                            f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
                        )
                        try:
                            shot.save(os.path.join(app.config['UPLOAD_FOLDER'], screenshot_filename))
                        except Exception as e:
                            logger.error(f"Screenshot save error: {e}")
                            screenshot_filename = None

            new_submission = Submission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                content=content,
                screenshot_filename=screenshot_filename,
                submitted_at=datetime.utcnow()
            )
            db.session.add(new_submission)
            db.session.commit()
        flash(_('HTML assignment submitted successfully!'))
        return redirect(url_for('student_dashboard'))
    except Exception as e:
        logger.error(f"submit_html_assignment {assignment_id} error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to submit assignment'))
        return redirect(url_for('view_assignment', assignment_id=assignment_id))


@app.route('/submit_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def submit_assignment(assignment_id):
    try:
        init_database()
        if request.method == 'POST':
            content = request.form.get('content', '').strip()
            if not content:
                flash(_('Content is required'))
                return redirect(url_for('view_assignment', assignment_id=assignment_id))
            with app.app_context():
                new_submission = Submission(
                    assignment_id=assignment_id,
                    student_id=current_user.id,
                    content=content
                )
                db.session.add(new_submission)
                db.session.commit()
            return render_template('assignment_submitted.html', assignment_id=assignment_id)
    except Exception as e:
        logger.error(f"submit_assignment {assignment_id} error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to submit assignment'))
    return redirect(url_for('view_assignment', assignment_id=assignment_id))


@app.route('/view_submissions/<int:assignment_id>')
@login_required
def view_submissions(assignment_id):
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    try:
        init_database()
        with app.app_context():
            assignment = Assignment.query.get_or_404(assignment_id)
            submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
        return render_template(
            'view_submissions.html',
            submissions=submissions,
            assignment=assignment
        )
    except Exception as e:
        logger.error(f"view_submissions {assignment_id} error: {e}", exc_info=True)
        flash(_('Error loading submissions'))
        return redirect(url_for('student_dashboard'))


@app.route('/grade_submission/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def grade_submission(submission_id):
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    try:
        init_database()
        with app.app_context():
            submission = Submission.query.get_or_404(submission_id)
            if request.method == 'POST':
                grade_str = request.form.get('grade', '')
                feedback = request.form.get('feedback', '')
                try:
                    submission.grade = float(grade_str) if grade_str else None
                    submission.feedback = feedback
                    db.session.commit()
                    flash(_('Submission graded successfully'))
                    return redirect(url_for('view_submissions', assignment_id=submission.assignment_id))
                except (ValueError, Exception) as e:
                    logger.error(f"grade error: {e}")
                    flash(_('Invalid grade or failed to save'))
    except Exception as e:
        logger.error(f"grade_submission {submission_id} error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Error grading submission'))
        with app.app_context():
            submission = Submission.query.get_or_404(submission_id)
    return render_template('grade_submission.html', submission=submission)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash(_('Password reset feature — please contact admin'))
    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        flash(_('Password reset feature — please contact admin'))
        return redirect(url_for('login'))
    return render_template('reset_password.html')


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    try:
        if request.method == 'POST':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            if not current_password or not new_password:
                flash(_('Both passwords are required'))
                return render_template('change_password.html')
            with app.app_context():
                if current_user.check_password(current_password):
                    current_user.set_password(new_password)
                    db.session.commit()
                    flash(_('Password changed successfully'))
                    return redirect(url_for('student_dashboard'))
                else:
                    flash(_('Current password is incorrect'))
    except Exception as e:
        logger.error(f"change_password error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to change password'))
    return render_template('change_password.html')


@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    try:
        init_database()
        with app.app_context():
            users = User.query.all()
        return render_template('admin_users.html', users=users)
    except Exception as e:
        logger.error(f"admin_users error: {e}", exc_info=True)
        flash(_('Error loading users'))
        return redirect(url_for('student_dashboard'))


@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if current_user.role != 'admin':
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    try:
        init_database()
        with app.app_context():
            user = User.query.get_or_404(user_id)
            if request.method == 'POST':
                user.username = request.form.get('username', user.username)
                user.email = request.form.get('email', user.email)
                user.role = request.form.get('role', user.role)
                new_pw = request.form.get('password', '')
                if new_pw:
                    user.set_password(new_pw)
                db.session.commit()
                flash(_('User updated successfully'))
                return redirect(url_for('admin_users'))
    except Exception as e:
        logger.error(f"admin_edit_user {user_id} error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to update user'))
        with app.app_context():
            user = User.query.get_or_404(user_id)
    return render_template('admin_edit_user.html', user=user)


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    try:
        init_database()
        with app.app_context():
            user = User.query.get_or_404(user_id)
            if user.id == current_user.id:
                flash(_('Cannot delete your own account'))
                return redirect(url_for('admin_users'))
            db.session.delete(user)
            db.session.commit()
        flash(_('User deleted successfully'))
    except Exception as e:
        logger.error(f"admin_delete_user {user_id} error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to delete user'))
    return redirect(url_for('admin_users'))


@app.route('/assignment/<int:assignment_id>/delete', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    try:
        init_database()
        with app.app_context():
            assignment = Assignment.query.get_or_404(assignment_id)
            if current_user.role != 'admin' and assignment.created_by != current_user.id:
                flash(_('You can only delete assignments that you created'))
                return redirect(url_for('student_dashboard'))

            Submission.query.filter_by(assignment_id=assignment_id).delete()
            db.session.execute(
                student_assignment.delete().where(
                    student_assignment.c.assignment_id == assignment_id
                )
            )
            db.session.delete(assignment)
            db.session.commit()
        flash(_('Assignment deleted successfully'))
    except Exception as e:
        logger.error(f"delete_assignment {assignment_id} error: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to delete assignment'))
    return redirect(url_for('student_dashboard'))


@app.route('/view_submission_content/<int:submission_id>')
@login_required
def view_submission_content(submission_id):
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))
    try:
        init_database()
        with app.app_context():
            submission = Submission.query.get_or_404(submission_id)
            safe_content = submission.content.replace('"', '&quot;')
            safe_username = submission.user.username.replace("'", "\\'") if submission.user else 'unknown'
            safe_title = submission.assignment.title.replace("'", "\\'") if submission.assignment else 'unknown'
            submission_date = submission.submitted_at.strftime('%Y-%m-%d_%H-%M') if submission.submitted_at else ''
            grade_display = f'{submission.grade}' if submission.grade else 'Not graded'
            feedback_display = submission.feedback if submission.feedback else ''
        html_doc = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Student Submission</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
.header {{ background: #4a6fa5; color: white; padding: 15px 20px; margin: -20px -20px 20px; box-shadow: 0 2px 4px rgba(0,0,0,.1); }}
.info {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,.1); }}
.content-box {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,.1); min-height: 400px; }}
.iframe {{ width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 4px; }}
.btn {{ background: #28a745; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; float: right; }}
.btn:hover {{ background: #218838; }}
</style>
</head>
<body>
<div class="header"><h1>Student Submission Details</h1></div>
<div class="info">
<button onclick="downloadIt()" class="btn">📥 Download</button>
<p><strong>Student:</strong> {submission.user.username if submission.user else 'N/A'}</p>
<p><strong>Assignment:</strong> {submission.assignment.title if submission.assignment else 'N/A'}</p>
<p><strong>Date:</strong> {submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if submission.submitted_at else 'N/A'}</p>
<p><strong>Grade:</strong> {grade_display}</p>
{'' if not feedback_display else f'<p><strong>Feedback:</strong> {feedback_display}</p>'}
</div>
<div class="content-box">
<h2>Student's Work</h2>
<div id="submissionContent" style="display:none;">{safe_content}</div>
<iframe srcdoc="{safe_content}" class="iframe"></iframe>
</div>
<script>
function downloadIt() {{
  const c = document.getElementById('submissionContent').innerHTML;
  const blob = new Blob([c], {{ type: 'text/html' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `{safe_username}_{safe_title}_{submission_date}.html`;
  document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}}
</script>
</body>
</html>
"""
        return html_doc
    except Exception as e:
        logger.error(f"view_submission_content {submission_id} error: {e}", exc_info=True)
        flash(_('Error loading submission'))
        return redirect(url_for('student_dashboard'))


# ──────────────────────────────────────────────────────────────
# __main__ — dev server only. Gunicorn never runs this.
# ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
