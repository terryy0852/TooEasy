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


# ── AI Services ────────────────────────────────────────────────
from ai_services import AIGradingService, AIServiceResult

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
# Force single Gunicorn worker (CSRF depends on one SECRET_KEY across all requests)
# Railway Nixpacks sets WEB_CONCURRENCY=cpu_count which breaks CSRF/sessions
# ──────────────────────────────────────────────────────────────
os.environ.setdefault('WEB_CONCURRENCY', '1')
os.environ.setdefault('MAX_WORKERS', '1')

# ──────────────────────────────────────────────────────────────
# Initialize Flask app
# ──────────────────────────────────────────────────────────────
app = Flask(__name__)

# Secret key MUST be EXPLICITLY set via env. Random key per worker = CSRF chaos
PRODUCTION_SECRET = os.environ.get('SECRET_KEY')
if PRODUCTION_SECRET and len(PRODUCTION_SECRET) > 20:
    app.secret_key = PRODUCTION_SECRET
    logger.info(f"Using SECRET_KEY from env ({len(PRODUCTION_SECRET)} chars)")
else:
    # Fallback - STATICALLY defined (NOT random per worker)
    # Critical for Gunicorn workers to share CSRF/session validation
    app.secret_key = 'too-easy-production-static-secret-key-2026-please-override-via-env'
    if PRODUCTION_SECRET:
        logger.warning(f"SECRET_KEY too short ({len(PRODUCTION_SECRET)}), using static fallback")
    else:
        logger.warning("SECRET_KEY not set via env — using static fallback (set env var for real security!)")

app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Session + CSRF configuration
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour token validity
app.config['WTF_CSRF_SSL_CHECKS'] = False  # Railway terminates SSL at edge
app.config['WTF_CSRF_METHODS'] = ['POST', 'PUT', 'PATCH', 'DELETE']
app.config['SESSION_COOKIE_NAME'] = 'tooeasy_session'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours for stability

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

@app.errorhandler(400)
def bad_request_error(error):
    logger.error(f"400 Bad Request: {error} — path={request.path} method={request.method}")
    logger.error(f"  session keys: {list(session.keys()) if session else 'EMPTY'}")
    logger.error(f"  form keys: {list(request.form.keys()) if request.form else 'EMPTY'}")
    logger.error(f"  form has csrf_token: {'csrf_token' in request.form if request.form else 'N/A'}")
    logger.error(f"  cookies: {list(request.cookies.keys()) if request.cookies else 'NONE'}")
    logger.error(f"  Referer: {request.headers.get('Referer', 'none')}")
    flash(f'CSRF or form validation failed. Please refresh the page and try again. [{str(error)[:60]}]')
    if request.method == 'POST' and 'csrf_token' in str(error):
        # Redirect back to GET of same route to regenerate fresh CSRF token
        return redirect(request.path)
    return render_template('error.html', error=f"Bad Request: {error}"), 400

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
# Fix Railway PostgreSQL URL format (postgres:// -> postgresql://)
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# ──────────────────────────────────────────────────────────────
# PRE-INIT DB URL PROBE (critical for broken Supabase URLs)
#
# Test the configured DATABASE_URL with a raw sqlalchemy engine +
# 5-second connect timeout BEFORE we hand it to Flask-SQLAlchemy.
# If the probe fails (DNS resolve error, auth, timeout, etc.),
# we silently swap the URI to local SQLite and set a flag.
#
# Why here: Flask-SQLAlchemy 3.x has db.engine as a read-only
# @property, and db.init_app() refuses to run twice on the same
# app.  So runtime rebinding is impossible.  Get it right FIRST.
# ──────────────────────────────────────────────────────────────
DB_USED_FALLBACK = False
FINAL_DB_URI = None

def _probe_db_uri(uri, is_pg, retries=3, delay=2):
    """Try to connect with retries; return True on success."""
    from sqlalchemy import create_engine, text as _text
    import time
    ca = {'connect_timeout': 15} if is_pg else {}
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            eng = create_engine(uri, connect_args=ca, future=True, pool_pre_ping=False)
            with eng.connect() as conn:
                conn.execute(_text('SELECT 1'))
            try:
                eng.dispose()
            except Exception:
                pass
            logger.info(f"[db_probe] ✅ Connected on attempt {attempt}")
            return True, None
        except Exception as e:
            last_err = e
            try:
                eng.dispose()
            except Exception:
                pass
            if attempt < retries:
                logger.warning(f"[db_probe] Attempt {attempt} failed, retrying in {delay}s...")
                time.sleep(delay)
    return False, last_err
    """Try to connect once (5s timeout); return True on success."""
    from sqlalchemy import create_engine, text as _text
    ca = {'connect_timeout': 5} if is_pg else {}
    try:
        eng = create_engine(uri, connect_args=ca, future=True, pool_pre_ping=False)
        with eng.connect() as conn:
            conn.execute(_text('SELECT 1'))
        try:
            eng.dispose()
        except Exception:
            pass
        return True, None
    except Exception as e:
        try:
            eng.dispose()
        except Exception:
            pass
        return False, e

if DATABASE_URL:
    # Try to reach the remote DATABASE_URL before committing to it
    # Railway internal DNS can be slow on first boot; allow override to trust it.
    is_pg = DATABASE_URL.startswith('postgresql')
    if os.environ.get('TRUST_DATABASE_URL', '').lower() in ('1', 'true', 'yes'):
        logger.info("[db_probe] TRUST_DATABASE_URL set — skipping probe, using configured URL")
        FINAL_DB_URI = DATABASE_URL
        app.config['SQLALCHEMY_DATABASE_URI'] = FINAL_DB_URI
        logger.info("[db_probe] ✅ Using PostgreSQL (trusted)")
    else:
        logger.info(f"[db_probe] Testing remote DATABASE_URL: {DATABASE_URL[:40]}...")
        probe_ok, probe_err = _probe_db_uri(DATABASE_URL, is_pg)
        if probe_ok:
            FINAL_DB_URI = DATABASE_URL
            app.config['SQLALCHEMY_DATABASE_URI'] = FINAL_DB_URI
            logger.info("[db_probe] ✅ Remote DB reachable, using PostgreSQL")
        else:
            logger.warning(
                f"[db_probe] ⚠️  Remote DB probe FAILED: {type(probe_err).__name__}: "
                f"{str(probe_err)[:200]} — falling back to SQLite"
            )
            DB_USED_FALLBACK = True
            FINAL_DB_URI = f'sqlite:///{os.path.join(instance_dir, "assignments.db")}'
            app.config['SQLALCHEMY_DATABASE_URI'] = FINAL_DB_URI
    # Try to reach the remote DATABASE_URL before committing to it
    is_pg = DATABASE_URL.startswith('postgresql')
    logger.info(f"[db_probe] Testing remote DATABASE_URL: {DATABASE_URL[:40]}...")
    probe_ok, probe_err = _probe_db_uri(DATABASE_URL, is_pg)
    if probe_ok:
        FINAL_DB_URI = DATABASE_URL
        app.config['SQLALCHEMY_DATABASE_URI'] = FINAL_DB_URI
        logger.info("[db_probe] ✅ Remote DB reachable, using PostgreSQL")
    else:
        logger.warning(
            f"[db_probe] ⚠️  Remote DB probe FAILED: {type(probe_err).__name__}: "
            f"{str(probe_err)[:200]} — falling back to SQLite"
        )
        DB_USED_FALLBACK = True
        FINAL_DB_URI = f'sqlite:///{os.path.join(instance_dir, "assignments.db")}'
        app.config['SQLALCHEMY_DATABASE_URI'] = FINAL_DB_URI
else:
    DB_USED_FALLBACK = True
    FINAL_DB_URI = f'sqlite:///{os.path.join(instance_dir, "assignments.db")}'
    app.config['SQLALCHEMY_DATABASE_URI'] = FINAL_DB_URI
    logger.info(f"[db_probe] No DATABASE_URL set, using SQLite: {FINAL_DB_URI}")

FINAL_DB_IS_PG = FINAL_DB_URI.startswith('postgresql')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {'connect_timeout': 10} if FINAL_DB_IS_PG else {},
}

db = SQLAlchemy(app)
# Runtime switch helper REMOVED — probe at module load ensures URI is final

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
    # ── AI Grading fields ────────────────────────────────────────
    answer_key = db.Column(db.Text, nullable=True)
    answer_key_filename = db.Column(db.String(255), nullable=True)
    ai_grading_enabled = db.Column(db.Boolean, default=False)
    grading_config = db.Column(db.Text, nullable=True)  # JSON config for future use

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
    # NOTE: grade column used to be db.Float.  We now accept letter grades
    # (A, B+, C-, F), numeric strings ("85", "92.5"), and "Pass/Fail".
    # Column type is String(32).  Retro-migration in init_database()
    # ALTERs any existing FLOAT-grade `submission` tables to TEXT/VARCHAR.
    grade = db.Column(db.String(32), nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    screenshot_filename = db.Column(db.String(255), nullable=True)
    # ── AI Grading fields ────────────────────────────────────────
    ai_grade = db.Column(db.String(32), nullable=True)
    ai_feedback = db.Column(db.Text, nullable=True)
    ai_graded_at = db.Column(db.DateTime, nullable=True)
    ai_grade_status = db.Column(db.String(20), nullable=True, default=None)  # pending/graded/failed
    ai_raw_response = db.Column(db.Text, nullable=True)  # full JSON for debugging

    assignment = db.relationship('Assignment', backref='submissions', lazy=True)
    user = db.relationship('User', backref='submissions', lazy=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.session_protection = 'basic'  # relaxed from 'strong' for Railway proxy

@login_manager.user_loader
def load_user(user_id):
    try:
        # Already inside a request context (Flask-Login calls this during request handling)
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"load_user error: {e}")
        return None

# ──────────────────────────────────────────────────────────────
# FIX 6: Lazy database init — runs ONCE on first request, safe
# __main__ block never runs under Gunicorn, so we use before_request.
#
# NOTE: DB_URL reachability was already validated AT MODULE LOAD
#       via _probe_db_uri().  db.engine is guaranteed configured
#       to a working endpoint (PostgreSQL reachable or local SQLite).
#       No runtime switching needed here — just tables + seed.
# ──────────────────────────────────────────────────────────────
_db_initialized = False


# ── AI Column Retro-Migration Helper ───────────────────────────
def _column_exists(table: str, col: str) -> bool:
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    return any(c['name'] == col for c in inspector.get_columns(table))


def _migrate_add_column(table: str, col: str, col_def: str):
    """Idempotently add a column if it doesn't exist."""
    try:
        if not _column_exists(table, col):
            if FINAL_DB_IS_PG:
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_def}"))
            else:
                try:
                    db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}"))
                except Exception:
                    pass
            db.session.commit()
            logger.info(f"[db_init] Added column {table}.{col}")
        else:
            logger.info(f"[db_init] Column {table}.{col} already exists")
    except Exception as e:
        logger.warning(f"[db_init] Column migration {table}.{col} skipped: {e}")
        try:
            db.session.rollback()
        except Exception:
            pass


def init_database():
    """Ensure tables exist, admin is seeded, and Submission.grade column is TEXT/STRING."""
    global _db_initialized
    if _db_initialized:
        return
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            if not existing_tables:
                logger.info("[db_init] Creating tables (grade column now STRING(32) for letter grades)...")
                db.create_all()
                logger.info("[db_init] Tables created")
            else:
                logger.info(f"[db_init] Tables exist: {existing_tables}")
                # ── Retro-migration: submission.grade FLOAT/REAL -> TEXT/VARCHAR ──
                # Old deployments created grade as db.Float; this prevents saving
                # letter grades ("A", "C", "B+") because SQLAlchemy's compiled
                # to_float processor ValueError's any non-numeric value during flush.
                # Conversion is driver-specific.
                if 'submission' in existing_tables:
                    try:
                        cols = inspector.get_columns('submission')
                        grade_col = next((c for c in cols if c['name'] == 'grade'), None)
                        current_type = None
                        if grade_col is not None:
                            t = grade_col['type']
                            current_type = str(t).lower() if t is not None else None
                        logger.info(f"[db_init] submission.grade column type: {current_type!r}")
                        needs_change = (
                            current_type is None
                            or any(k in current_type for k in ['float', 'real', 'numeric', 'double'])
                        )
                        if needs_change:
                            if FINAL_DB_IS_PG:
                                # PostgreSQL: one-shot ALTER COLUMN ... TYPE VARCHAR(32) USING grade::text
                                logger.info("[db_init] Postgres: ALTER COLUMN submission.grade -> VARCHAR(32)")
                                db.session.execute(text(
                                    "ALTER TABLE submission "
                                    "ALTER COLUMN grade TYPE VARCHAR(32) "
                                    "USING grade::text"
                                ))
                                db.session.commit()
                                logger.info("[db_init] submission.grade converted to VARCHAR(32) on Postgres")
                            else:
                                # SQLite: no ALTER COLUMN TYPE, so:
                                #   1) BEGIN
                                #   2) create tmp_submission NEW schema (grade TEXT)
                                #   3) copy rows old->new (CAST grade AS TEXT)
                                #   4) DROP old; rename new->submission
                                #   5) COMMIT
                                logger.info("[db_init] SQLite: rebuild submission table with grade TEXT")
                                db.session.execute(text("BEGIN"))
                                db.session.execute(text(
                                    "CREATE TABLE submission_new ("
                                    "id INTEGER PRIMARY KEY, "
                                    "assignment_id INTEGER NOT NULL, "
                                    "student_id INTEGER NOT NULL, "
                                    "content TEXT NOT NULL, "
                                    "submitted_at DATETIME, "
                                    "grade TEXT, "
                                    "feedback TEXT, "
                                    "screenshot_filename VARCHAR(255), "
                                    "FOREIGN KEY(assignment_id) REFERENCES assignment(id), "
                                    "FOREIGN KEY(student_id) REFERENCES user(id))"
                                ))
                                db.session.execute(text(
                                    "INSERT INTO submission_new "
                                    "(id, assignment_id, student_id, content, submitted_at, "
                                    " grade, feedback, screenshot_filename) "
                                    "SELECT id, assignment_id, student_id, content, submitted_at, "
                                    "       CAST(grade AS TEXT), feedback, screenshot_filename "
                                    "FROM submission"
                                ))
                                db.session.execute(text("DROP TABLE submission"))
                                db.session.execute(text("ALTER TABLE submission_new RENAME TO submission"))
                                db.session.commit()
                                logger.info("[db_init] submission table rebuilt on SQLite with grade TEXT")
                        else:
                            logger.info("[db_init] submission.grade already TEXT/VARCHAR; no migration needed")
                    except Exception as me:
                        logger.error(f"[db_init] grade migration SKIPPED due to error: {me}", exc_info=True)
                        try:
                            db.session.rollback()
                        except Exception:
                            pass

            # ── Retro-migrate AI columns ────────────────────────────────
            if 'assignment' in existing_tables:
                _migrate_add_column('assignment', 'answer_key', 'TEXT')
                _migrate_add_column('assignment', 'answer_key_filename', 'VARCHAR(255)')
                _migrate_add_column('assignment', 'ai_grading_enabled', 'BOOLEAN DEFAULT FALSE')
                _migrate_add_column('assignment', 'grading_config', 'TEXT')
            if 'submission' in existing_tables:
                _migrate_add_column('submission', 'ai_grade', 'VARCHAR(32)')
                _migrate_add_column('submission', 'ai_feedback', 'TEXT')
                _migrate_add_column('submission', 'ai_graded_at', 'DATETIME')
                _migrate_add_column('submission', 'ai_grade_status', 'VARCHAR(20)')
                _migrate_add_column('submission', 'ai_raw_response', 'TEXT')

            # ── Seed test users (never lost on new containers) ────────────
            # Railway containers have ephemeral filesystems: on each deploy,
            #   /app/instance/assignments.db is a brand-new SQLite file, so
            #   users manually registered last deploy are lost.
            # We solve this with DETERMINISTIC RE-SEEDING: each fresh DB boot
            #   recreates the users listed below if they don't already exist.
            # New students/teachers you add via /register still have to be
            #   added here if you want them to survive deploy rebuilds, OR
            #   use persistent storage (see instructions after this block).
            SEED_USERS = [
                # dict keys match User constructor args + password plaintext
                dict(username='admin', email='admin@example.com', role='admin', password='admin123'),
                dict(username='SY',    email='youngsteve0212@gmail.com', role='student', password='password123'),
                dict(username='tutor1',email='tutor1@example.com',       role='teacher', password='teacher123'),
            ]
            created = 0
            for u in SEED_USERS:
                exists = User.query.filter_by(username=u['username']).first()
                if exists is None:
                    try:
                        user = User(
                            username=u['username'],
                            email=u['email'],
                            role=u['role'],
                        )
                        user.set_password(u['password'])
                        db.session.add(user)
                        db.session.commit()
                        created += 1
                        logger.info(
                            f"[db_init] Seed user: u={u['username']} role={u['role']} p={u['password']}"
                        )
                    except Exception as se:
                        db.session.rollback()
                        logger.warning(f"[db_init] seed {u['username']} failed: {se}")
            if created > 0:
                logger.info(f"[db_init] Re-seeded {created} user(s) on fresh DB boot")
            # Also: always guarantee admin exists even if not in SEED_USERS (belt & suspenders)
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                try:
                    admin_user = User(username='admin', email='admin@example.com', role='admin')
                    admin_user.set_password('admin123')
                    db.session.add(admin_user)
                    db.session.commit()
                    logger.info("[db_init] Admin user seeded (u=admin / p=admin123)")
                except Exception as se:
                    db.session.rollback()
                    logger.warning(f"[db_init] seed admin failed: {se}")
        _db_initialized = True
        db_kind = 'PostgreSQL' if FINAL_DB_IS_PG else 'SQLite'
        fb = " (remote unreachable -> SQLite fallback)" if DB_USED_FALLBACK else ""
        logger.info(f"[db_init] ✅ Database initialization complete [{db_kind}]{fb}")
    except Exception as e:
        logger.critical(f"[db_init] ❌ FAILED: {e}", exc_info=True)
        raise


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
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        db_kind = 'postgresql' if db_uri.startswith('postgresql') else ('sqlite' if db_uri.startswith('sqlite') else 'unknown')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'db': 'ok',
            'db_kind': db_kind,
            'db_used_fallback': DB_USED_FALLBACK,
            'version': '1.3-preinit-probe'
        }), 200
    except Exception as e:
        logger.error(f"Health check FAIL: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'db_used_fallback': DB_USED_FALLBACK,
            'version': '1.3-preinit-probe'
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
# CRITICAL: Flask routes already have an app_context and request context.
# NEVER use `with app.app_context():` inside a route — it pushes a NEW context
# with a FRESH scoped db.session, causing "Instance not bound to session" errors
# when models become DETACHED after the inner context exits.
# Use db queries directly in the route body; they'll use the existing scoped session.
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
            logger.info(f"[login] POST received — user='{username}' csrf_in_form={'csrf_token' in request.form} session_cookie_present={'tooeasy_session' in request.cookies}")
            if not username or not password:
                flash(_('Username and password are required'))
                return render_template('login.html')

            user = User.query.filter_by(username=username).first()
            logger.info(f"[login] query result: user={('found id='+str(user.id)+' role='+user.role) if user else 'NOT FOUND'}")
            if user and user.check_password(password):
                login_user(user, remember=True)
                session.permanent = True
                logger.info(f"[login] SUCCESS — user={username} logged in, redirecting to dashboard")
                flash(_('Login successful!'))
                return redirect(url_for('student_dashboard'))
            else:
                logger.warning(f"[login] FAIL — invalid credentials for username='{username}'")
                flash(_('Invalid username or password'))
    except Exception as e:
        logger.error(f"[login] ROUTE ERROR: {type(e).__name__}: {e}", exc_info=True)
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
            logger.info(f"[register] POST — user='{username}' email='{email}' role='{role}' csrf_in_form={'csrf_token' in request.form}")

            if not username or not email or not password:
                flash(_('All fields are required'))
                return render_template('register.html')

            logger.debug(f"[register] checking duplicate username '{username}'...")
            if User.query.filter_by(username=username).first():
                logger.warning(f"[register] username already exists: {username}")
                flash(_('Username already exists'))
                return render_template('register.html')
            logger.debug(f"[register] checking duplicate email '{email}'...")
            if User.query.filter_by(email=email).first():
                logger.warning(f"[register] email already registered: {email}")
                flash(_('Email already registered'))
                return render_template('register.html')

            logger.info(f"[register] creating User model...")
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)
            logger.info(f"[register] password hashed, adding to session...")
            db.session.add(new_user)
            logger.info(f"[register] calling db.session.commit()...")
            db.session.commit()
            logger.info(f"[register] ✅ COMMIT OK — new user id={new_user.id}")

            flash(_('Registration successful! Please login.'))
            return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"[register] ❌ ROUTE ERROR: {type(e).__name__}: {e}", exc_info=True)
        try:
            db.session.rollback()
            logger.info("[register] session rolled back")
        except Exception as rb:
            logger.error(f"[register] rollback failed: {rb}")
        flash(_('Registration failed. Please try again.'))
    return render_template('register.html')


@app.route('/student_dashboard')
@login_required
def student_dashboard():
    try:
        init_database()
        logger.debug(f"[dashboard] user={current_user.username} role={current_user.role}")
        if current_user.role == 'student':
            assignments = Assignment.query.join(
                student_assignment,
                Assignment.id == student_assignment.c.assignment_id
            ).filter(
                student_assignment.c.student_id == current_user.id,
                Assignment.is_active == True
            ).all()
            assignment_submissions = {}
            # Pass plain dicts (not ORM proxy objects) to the template.
            # Jinja's `{% if sub.grade is not none %}` sometimes mis-fires when
            # grade is a SQLAlchemy ColumnProperty loaded lazily via scoped session
            # descriptor; flat Python dict values avoid that ambiguity entirely.
            for a in assignments:
                sub = Submission.query.filter_by(
                    assignment_id=a.id, student_id=current_user.id
                ).first()
                if sub is not None:
                    # Grade column stored as string ("A", "B+", "85", "C-") OR
                    # legacy float (85.0, 0.0). Normalize to str-or-None plain value
                    # so Jinja `{% if grade is not none %}` is always unambiguous.
                    if sub.grade is None:
                        grade_val = None
                    else:
                        grade_val = str(sub.grade).strip()
                        if grade_val == '':
                            grade_val = None
                    sub_dict = {
                        'id': sub.id,
                        'assignment_id': sub.assignment_id,
                        'content': sub.content,
                        'submitted_at': sub.submitted_at,
                        'grade': grade_val,
                        'feedback': sub.feedback,
                    }
                    assignment_submissions[a.id] = sub_dict
                    logger.info(
                        f"[dashboard] student={current_user.username} "
                        f"assignment_id={a.id} sub_id={sub.id} "
                        f"grade={grade_val!r} feedback_len={len(sub.feedback or '')}"
                    )
                else:
                    assignment_submissions[a.id] = None
            return render_template(
                'student_dashboard.html',
                assignments=assignments,
                assignment_submissions=assignment_submissions
            )
        else:
            assignments = Assignment.query.all()
            return render_template('student_dashboard.html', assignments=assignments)
    except Exception as e:
        logger.error(f"[dashboard] ERROR: {type(e).__name__}: {e}", exc_info=True)
        flash(_('Error loading dashboard'))
        return redirect(url_for('login'))



# ── Answer Key Extraction Helper ───────────────────────────────
def _extract_answer_key_from_html(html_text: str) -> str:
    """
    Extract filled-in answers from a teacher's completed HTML worksheet.
    Parses input values, selected options, checked boxes, and textarea content.
    """
    from html.parser import HTMLParser

    class AnswerExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.answers = []
            self.current_tag = None
            self.current_attrs = {}
            self.in_textarea = False
            self.textarea_content = []

        def handle_starttag(self, tag, attrs):
            self.current_tag = tag
            self.current_attrs = dict(attrs)

            if tag == 'input':
                input_type = self.current_attrs.get('type', 'text')
                name = self.current_attrs.get('name', '')
                value = self.current_attrs.get('value', '')
                checked = 'checked' in self.current_attrs

                if input_type in ('checkbox', 'radio'):
                    if checked:
                        self.answers.append(f"{name}: [CHECKED] {value}")
                elif value.strip():
                    self.answers.append(f"{name}: {value}")

            elif tag == 'select':
                self.current_select_name = self.current_attrs.get('name', '')
                self.select_options = []

            elif tag == 'option':
                selected = 'selected' in self.current_attrs
                value = self.current_attrs.get('value', '')
                if selected and value:
                    self.answers.append(f"{getattr(self, 'current_select_name', '')}: {value}")

            elif tag == 'textarea':
                self.in_textarea = True
                self.textarea_name = self.current_attrs.get('name', '')
                self.textarea_content = []

        def handle_endtag(self, tag):
            if tag == 'textarea' and self.in_textarea:
                content = ''.join(self.textarea_content).strip()
                if content:
                    self.answers.append(f"{self.textarea_name}: {content}")
                self.in_textarea = False

        def handle_data(self, data):
            if self.in_textarea:
                self.textarea_content.append(data)

    try:
        parser = AnswerExtractor()
        parser.feed(html_text)
        if parser.answers:
            return "\n".join(parser.answers)
    except Exception:
        pass

    # Fallback: if no structured answers found, return first 8000 chars as plain text
    plain = re.sub(r'<[^>]+>', ' ', html_text)
    plain = re.sub(r'\s+', ' ', plain).strip()
    return plain[:8000]


@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if current_user.role not in ['admin', 'teacher']:
        flash(_('Access denied'))
        return redirect(url_for('student_dashboard'))

    try:
        init_database()
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

            answer_key = request.form.get('answer_key', '').strip()
            ai_grading_enabled = 'ai_grading_enabled' in request.form
            answer_key_file = request.files.get('answer_key_file')
            answer_key_filename = None

            # If teacher uploaded a marking scheme / answer file, extract answers
            if answer_key_file and answer_key_file.filename:
                try:
                    key_content = answer_key_file.read().decode('utf-8')
                    if answer_key_file.filename.lower().endswith('.html'):
                        extracted = _extract_answer_key_from_html(key_content)
                        if extracted:
                            answer_key = extracted
                            answer_key_filename = answer_key_file.filename
                    else:
                        # Plain text / markdown — use as-is (truncated)
                        answer_key = key_content.strip()[:12000]
                        answer_key_filename = answer_key_file.filename
                except Exception as e:
                    logger.warning(f"[create_assignment] Could not read answer key file: {e}")

            new_assignment = Assignment(
                title=title,
                description=description,
                created_by=current_user.id,
                due_date=due_date,
                is_active=is_active,
                answer_key=answer_key,
                answer_key_filename=answer_key_filename,
                ai_grading_enabled=ai_grading_enabled
            )
            db.session.add(new_assignment)
            db.session.flush()

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
                        logger.error(f"[create_assignment] HTML save error: {e}")
                        flash(_('Could not save HTML file'))
                        db.session.rollback()
                        return render_template('create_assignment.html', students=students)
                else:
                    flash(_('Only HTML files are allowed'))
                    return render_template('create_assignment.html', students=students)

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
        logger.error(f"[create_assignment] ERROR: {type(e).__name__}: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to create assignment'))
        students = User.query.filter_by(role='student').all()
    return render_template('create_assignment.html', students=students)


@app.route('/view_assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    try:
        init_database()
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
        logger.error(f"[view_assignment {assignment_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
        flash(_('Error loading assignment'))
        return redirect(url_for('student_dashboard'))


@app.route('/submit_html_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def submit_html_assignment(assignment_id):
    if request.method != 'POST':
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    try:
        init_database()
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
                        logger.error(f"[submit_html] Screenshot save error: {e}")
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
        logger.error(f"[submit_html {assignment_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
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
            new_submission = Submission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                content=content
            )
            db.session.add(new_submission)
            db.session.commit()
            return render_template('assignment_submitted.html', assignment_id=assignment_id)
    except Exception as e:
        logger.error(f"[submit_assignment {assignment_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
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
        assignment = Assignment.query.get_or_404(assignment_id)
        submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
        return render_template(
            'view_submissions.html',
            submissions=submissions,
            assignment=assignment
        )
    except Exception as e:
        logger.error(f"[view_submissions {assignment_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
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
        submission = Submission.query.get_or_404(submission_id)
        logger.info(f"[grade {submission_id}] user={current_user.username} role={current_user.role} method={request.method} student={submission.user.username} assignment_id={submission.assignment_id}")
        if request.method == 'POST':
            grade_raw = (request.form.get('grade', '') or '').strip()
            feedback = request.form.get('feedback', '') or ''
            csrf_ok = 'csrf_token' in request.form
            logger.info(f"[grade {submission_id}] POST — grade='{grade_raw}' feedback_len={len(feedback)} csrf_in_form={csrf_ok}")

            # ── Validation FIRST (before any session mutations) ─────────────
            # Accept: numbers (0-100, decimals), letter grades (A-F), with +/-
            #   examples: 85, 92.5, A, B+, C-, F, P, Pass
            # Reject: empty after strip cannot be graded (leave as pending);
            #         > 20 chars is likely garbage
            validation_errors = []
            if grade_raw == '':
                normalized_grade = None
            elif len(grade_raw) > 20:
                validation_errors.append(f"Grade too long ({len(grade_raw)} > 20 chars)")
            else:
                normalized_grade = grade_raw

            if validation_errors:
                for msg in validation_errors:
                    logger.warning(f"[grade {submission_id}] VALIDATION FAIL: {msg}")
                    flash(_(f"Invalid grade: {validation_errors[0]}"))
            else:
                # ── Commit once ─────────────────────────────────────────────
                try:
                    submission.grade = normalized_grade
                    submission.feedback = feedback
                    logger.info(
                        f"[grade {submission_id}] persisting grade={normalized_grade!r} "
                        f"feedback_len={len(feedback)}"
                    )
                    db.session.commit()
                    db.session.refresh(submission)
                    logger.info(
                        f"[grade {submission_id}] ✅ COMMIT + REFRESH OK — "
                        f"grade_in_DB={submission.grade!r} student={submission.user.username}"
                    )
                    flash(_('Submission graded successfully'))
                    return redirect(url_for('view_submissions', assignment_id=submission.assignment_id))
                except Exception as e:
                    logger.error(
                        f"[grade {submission_id}] DB commit FAIL: {type(e).__name__}: {e}",
                        exc_info=True,
                    )
                    try:
                        db.session.rollback()
                    except Exception:
                        pass
                    flash(_('Failed to save grade — please try again'))
    except Exception as e:
        logger.error(f"[grade_submission {submission_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        flash(_('Error grading submission'))
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
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                db.session.commit()
                flash(_('Password changed successfully'))
                return redirect(url_for('student_dashboard'))
            else:
                flash(_('Current password is incorrect'))
    except Exception as e:
        logger.error(f"[change_password] ERROR: {type(e).__name__}: {e}", exc_info=True)
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
        users = User.query.all()
        return render_template('admin_users.html', users=users)
    except Exception as e:
        logger.error(f"[admin_users] ERROR: {type(e).__name__}: {e}", exc_info=True)
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
        logger.error(f"[admin_edit_user {user_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
        db.session.rollback()
        flash(_('Failed to update user'))
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
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            flash(_('Cannot delete your own account'))
            return redirect(url_for('admin_users'))
        db.session.delete(user)
        db.session.commit()
        flash(_('User deleted successfully'))
    except Exception as e:
        logger.error(f"[admin_delete_user {user_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
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
        logger.error(f"[delete_assignment {assignment_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
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
        logger.error(f"[view_submission_content {submission_id}] ERROR: {type(e).__name__}: {e}", exc_info=True)
        flash(_('Error loading submission'))
        return redirect(url_for('student_dashboard'))


# ──────────────────────────────────────────────────────────────

# ═══════════════════════════════════════════════════════════════
# AI GRADING ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/grade_submission/<int:submission_id>', methods=['POST'])
@login_required
def api_grade_submission(submission_id):
    """Trigger AI grading for a single submission."""
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    try:
        init_database()
        submission = Submission.query.get_or_404(submission_id)
        assignment = submission.assignment

        if not assignment.ai_grading_enabled:
            return jsonify({'success': False, 'error': 'AI grading not enabled for this assignment'}), 400
        if not assignment.answer_key:
            return jsonify({'success': False, 'error': 'No answer key set for this assignment'}), 400

        submission.ai_grade_status = 'pending'
        db.session.commit()

        service = AIGradingService()
        result = service.execute(
            answer_key=assignment.answer_key,
            student_html=submission.content,
            max_score=100,
            assignment_title=assignment.title,
        )

        if result.success:
            submission.ai_grade = result.data.get('grade', '')
            submission.ai_feedback = result.data.get('feedback', '')
            submission.ai_graded_at = datetime.utcnow()
            submission.ai_grade_status = 'graded'
            submission.ai_raw_response = result.raw_response
            db.session.commit()
            logger.info(f"[ai_grade] submission_id={submission_id} grade={submission.ai_grade}")
            return jsonify({
                'success': True,
                'grade': submission.ai_grade,
                'feedback': submission.ai_feedback,
                'confidence': result.data.get('confidence', 'medium'),
                'tokens_used': result.tokens_used,
            })
        else:
            submission.ai_grade_status = 'failed'
            db.session.commit()
            logger.error(f"[ai_grade] submission_id={submission_id} failed: {result.error}")
            return jsonify({'success': False, 'error': result.error}), 500

    except Exception as e:
        logger.error(f"[api_grade_submission {submission_id}] ERROR: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/grade_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def api_grade_assignment(assignment_id):
    """Batch AI-grade all ungraded submissions for an assignment."""
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    try:
        init_database()
        assignment = Assignment.query.get_or_404(assignment_id)
        if not assignment.ai_grading_enabled:
            return jsonify({'success': False, 'error': 'AI grading not enabled'}), 400
        if not assignment.answer_key:
            return jsonify({'success': False, 'error': 'No answer key'}), 400

        submissions = Submission.query.filter_by(
            assignment_id=assignment_id,
            ai_grade_status=None,
        ).all()

        service = AIGradingService()
        graded_count = 0
        failed_count = 0

        for sub in submissions:
            sub.ai_grade_status = 'pending'
            db.session.commit()
            result = service.execute(
                answer_key=assignment.answer_key,
                student_html=sub.content,
                max_score=100,
                assignment_title=assignment.title,
            )
            if result.success:
                sub.ai_grade = result.data.get('grade', '')
                sub.ai_feedback = result.data.get('feedback', '')
                sub.ai_graded_at = datetime.utcnow()
                sub.ai_grade_status = 'graded'
                sub.ai_raw_response = result.raw_response
                graded_count += 1
            else:
                sub.ai_grade_status = 'failed'
                failed_count += 1
            db.session.commit()

        return jsonify({
            'success': True,
            'graded': graded_count,
            'failed': failed_count,
        })
    except Exception as e:
        logger.error(f"[api_grade_assignment {assignment_id}] ERROR: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/accept_ai_grade/<int:submission_id>', methods=['POST'])
@login_required
def api_accept_ai_grade(submission_id):
    """Teacher accepts the AI-generated grade as the final grade."""
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    try:
        init_database()
        submission = Submission.query.get_or_404(submission_id)
        if submission.ai_grade_status != 'graded':
            return jsonify({'success': False, 'error': 'No AI grade available'}), 400

        submission.grade = submission.ai_grade
        submission.feedback = submission.ai_feedback
        db.session.commit()
        logger.info(f"[accept_ai_grade] submission_id={submission_id} accepted")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"[accept_ai_grade {submission_id}] ERROR: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai_health', methods=['GET'])
@login_required
def ai_health():
    """Check AI service connectivity."""
    try:
        service = AIGradingService()
        ok = service.health_check()
        return jsonify({'healthy': ok, 'service': 'AIGradingService'})
    except Exception as e:
        return jsonify({'healthy': False, 'error': str(e)}), 500

# __main__ — dev server only. Gunicorn never runs this.
# ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
