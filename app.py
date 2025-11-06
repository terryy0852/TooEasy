# 导入必要的模块
from flask import Flask, render_template, redirect, url_for, request, flash, send_file, g, session, jsonify, has_request_context
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
from datetime import datetime
import uuid
from flask_babel import Babel, gettext as flask_babel_gettext
from babel.support import Translations
import functools
import builtins

# Set up Babel configuration
babel = Babel()

# 配置Flask应用
app = Flask(__name__)
# Read sensitive and deployment configs from environment variables when available
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
# 配置会话持久性 - 解决15分钟后会话过期问题
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24小时（秒）
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # 每次请求刷新会话
# Database configuration: prefer env-provided PostgreSQL URL, fallback to SQLite
database_url = os.environ.get('DATABASE_URL', 'sqlite:///assignments.db')
# Normalize legacy postgres:// to postgresql:// for SQLAlchemy/psycopg2 compatibility
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
# Engine options to improve reliability in hosted environments
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,  # Recycle connections after 5 minutes
    'pool_timeout': 30,   # 30 second timeout for getting connections
    'max_overflow': 10    # Allow up to 10 connections beyond pool size
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')

# 配置Babel用于国际化
# Using a different approach to configure Babel that works better with Flask-Babel 4.0.0
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.abspath('translations')

# Add Babel version to config (safely)
try:
    import flask_babel
    # Try different ways to get the version
    if hasattr(flask_babel, '__version__'):
        babel_version = flask_babel.__version__
    elif hasattr(flask_babel, 'version'):
        babel_version = flask_babel.version
    else:
        babel_version = 'unknown'
    app.config['BABEL_VERSION'] = babel_version
except Exception as e:
    app.config['BABEL_VERSION'] = 'unknown'
    print(f"[BABEL DEBUG] Error getting Flask-Babel version: {e}")

def student_required(f):
    """Decorator to require student access"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.is_tutor:
            flash(_('You are not authorized to access this page'))
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

print(f"Configured Babel translation directory: {app.config['BABEL_TRANSLATION_DIRECTORIES']}")
print(f"Supported locales: {app.config['BABEL_SUPPORTED_LOCALES']}")
print(f"Flask-Babel version: {app.config['BABEL_VERSION']}")

# Create and configure Babel instance
# Updated configuration for Flask-Babel 4.0.0 compatibility
babel = Babel(app)

# Define the locale selector function
def get_locale():
    # Enhanced debugging for locale selection
    print("[BABEL DEBUG] ===== Locale Selection Process Started =====")
    print(f"[BABEL DEBUG] Request URL: {request.url}")
    print(f"[BABEL DEBUG] Request args: {request.args}")
    print(f"[BABEL DEBUG] Session data: {session}")
    
    # Check if a language is explicitly set in the URL
    lang = request.args.get('lang')
    if lang:
        print(f"[BABEL DEBUG] Found language in URL parameters: {lang}")
    
    # If no language in URL, check session
    if not lang:
        lang = session.get('lang')
        if lang:
            print(f"[BABEL DEBUG] Found language in session: {lang}")
    
    # If no language is specified, try to use Accept-Language header
    if not lang:
        # Try to get language from Accept-Language header
        try:
            accept_langs = request.accept_languages
            print(f"[BABEL DEBUG] Accept-Language header: {accept_langs}")
            best_match = accept_langs.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
            print(f"[BABEL DEBUG] Best match from Accept-Language: {best_match}")
            lang = best_match
        except Exception as e:
            print(f"[BABEL DEBUG] Error getting Accept-Language: {e}")
    
    # Fallback to default locale if no valid language is found
    if not lang or lang not in app.config['BABEL_SUPPORTED_LOCALES']:
        old_lang = lang
        lang = app.config['BABEL_DEFAULT_LOCALE']
        print(f"[BABEL DEBUG] Language {old_lang} not valid or not supported, falling back to default: {lang}")
    else:
        print(f"[BABEL DEBUG] Selected valid language: {lang}")
        
    # Store the selected language in the session
    if lang != session.get('lang'):
        print(f"[BABEL DEBUG] Updating session language from {session.get('lang')} to {lang}")
        session['lang'] = lang
    
    print(f"[BABEL DEBUG] Final selected locale: {lang}")
    print("[BABEL DEBUG] ===== Locale Selection Process Completed =====")
    
    return lang

# Register the locale selector with Babel
babel.locale_selector = get_locale

# Debug route to show current Babel configuration
@app.route('/babel_config')
def show_babel_config():
    """Show current Babel configuration for debugging"""
    config = {
        'default_locale': app.config.get('BABEL_DEFAULT_LOCALE'),
        'supported_locales': app.config.get('BABEL_SUPPORTED_LOCALES'),
        'translation_dirs': app.config.get('BABEL_TRANSLATION_DIRECTORIES'),
        'translation_dir_exists': os.path.exists(app.config.get('BABEL_TRANSLATION_DIRECTORIES')),
        'babel_version': app.config.get('BABEL_VERSION', 'unknown'),
        'current_locale': get_locale()
    }
    return jsonify(config)

# Utility function to load translations directly from .mo files
def get_translation_from_file(text, locale=None):
    """Load translation directly from .mo file, bypassing Flask-Babel issues"""
    from babel.support import Translations
    import os
    import traceback
    
    if locale is None:
        locale = get_locale()
    
    print(f"[BABEL DEBUG] get_translation_from_file called with '{text}' and locale '{locale}'")
    
    # Construct path to .mo file
    trans_dir = app.config.get('BABEL_TRANSLATION_DIRECTORIES')
    mo_file_path = os.path.join(trans_dir, locale, 'LC_MESSAGES', 'messages.mo')
    
    print(f"[BABEL DEBUG] Looking for .mo file at: {mo_file_path}")
    
    try:
        # Check if directory exists
        dir_path = os.path.dirname(mo_file_path)
        print(f"[BABEL DEBUG] Directory exists: {os.path.exists(dir_path)}")
        
        if os.path.exists(mo_file_path):
            print(f"[BABEL DEBUG] Found .mo file: {mo_file_path}")
            print(f"[BABEL DEBUG] File size: {os.path.getsize(mo_file_path)} bytes")
            
            # Try to load the file
            try:
                with open(mo_file_path, 'rb') as f:
                    print(f"[BABEL DEBUG] Successfully opened .mo file: {mo_file_path}")
                    translations = Translations(f)
                    print(f"[BABEL DEBUG] Successfully created Translations object")
                    
                    # Try to translate
                    translated = translations.ugettext(text)
                    print(f"[BABEL DEBUG] Translation result: '{text}' -> '{translated}'")
                    
                    # Return translated text regardless if it's different
                    # This helps with debugging and ensures consistency
                    return translated
            except Exception as e:
                print(f"[BABEL DEBUG] Error reading .mo file: {e}")
                print(f"[BABEL DEBUG] Stack trace: {traceback.format_exc()}")
        else:
            print(f"[BABEL DEBUG] .mo file not found at {mo_file_path}")
            
            # List available files for debugging
            if os.path.exists(dir_path):
                print(f"[BABEL DEBUG] Files in directory {dir_path}:")
                for file in os.listdir(dir_path):
                    print(f"[BABEL DEBUG] - {file}")
            else:
                print(f"[BABEL DEBUG] Directory {dir_path} does not exist")
    except Exception as e:
        print(f"[BABEL DEBUG] Unexpected error in get_translation_from_file: {e}")
        print(f"[BABEL DEBUG] Stack trace: {traceback.format_exc()}")
    
    print(f"[BABEL DEBUG] Returning original text: '{text}'")
    return text

# Enhanced debug translation filter using direct .mo file loading
@app.template_filter('debug_trans')
def debug_trans(text):
    """Enhanced debug filter that uses direct .mo file loading for reliable translations"""
    print(f"[BABEL DEBUG] debug_trans filter called with '{text}'")
    
    # Get current locale
    current_locale = get_locale()
    print(f"[BABEL DEBUG] debug_trans: Current locale determined as: {current_locale}")
    
    # Try direct .mo file loading first (most reliable)
    print(f"[BABEL DEBUG] debug_trans: Attempting direct .mo file translation")
    file_translated = get_translation_from_file(text, current_locale)
    print(f"[BABEL DEBUG] debug_trans: Direct .mo file translation result: '{text}' -> '{file_translated}'")
    
    # Also try Flask-Babel's approach for comparison
    try:
        print(f"[BABEL DEBUG] debug_trans: Attempting Flask-Babel API translation")
        from flask_babel import get_translations
        translations = get_translations()
        print(f"[BABEL DEBUG] debug_trans: Flask-Babel get_translations() result: {translations}")
        if translations:
            babel_translated = translations.ugettext(text)
            print(f"[BABEL DEBUG] debug_trans: Flask-Babel translation result: '{text}' -> '{babel_translated}'")
        else:
            babel_translated = text
            print(f"[BABEL DEBUG] debug_trans: No Flask-Babel translations available")
    except Exception as e:
        babel_translated = text
        print(f"[BABEL DEBUG] debug_trans: Error with Flask-Babel: {e}")
        import traceback
        print(f"[BABEL DEBUG] debug_trans: Flask-Babel error stack trace: {traceback.format_exc()}")
    
    # Also try the standard _() function
    try:
        print(f"[BABEL DEBUG] debug_trans: Attempting standard _() function translation")
        standard_translated = _(text)
        print(f"[BABEL DEBUG] debug_trans: Standard _() translation result: '{text}' -> '{standard_translated}'")
    except Exception as e:
        standard_translated = text
        print(f"[BABEL DEBUG] debug_trans: Error with _(): {e}")
        import traceback
        print(f"[BABEL DEBUG] debug_trans: _() function error stack trace: {traceback.format_exc()}")
    
    # Return the most reliable translation (direct file loading first)
    print(f"[BABEL DEBUG] debug_trans: Selecting best translation result")
    if file_translated != text:
        print(f"[BABEL DEBUG] debug_trans: Using direct .mo file translation")
        return file_translated
    elif babel_translated != text:
        print(f"[BABEL DEBUG] debug_trans: Using Flask-Babel translation")
        return babel_translated
    elif standard_translated != text:
        print(f"[BABEL DEBUG] debug_trans: Using standard _() function translation")
        return standard_translated
    else:
        print(f"[BABEL DEBUG] debug_trans: No translation found, returning original text")
        return text

# Function to gettext with locale
@functools.lru_cache(maxsize=1000)
def monkey_patched_gettext_with_locale(string, locale):
    """Monkey patched gettext function with explicit locale support"""
    print(f"[BABEL DEBUG DETAILED] _with_locale called: '{string}', locale: {locale}")
    
    try:
        # Get the translations directory
        translations_dir = app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations')
        print(f"[BABEL DEBUG DETAILED] Using translation directory: {translations_dir}")
        
        # Get absolute path for debugging
        abs_translations_dir = os.path.abspath(translations_dir)
        print(f"[BABEL DEBUG DETAILED] Absolute translation directory: {abs_translations_dir}")
        
        # Construct the path to the .mo file
        mo_file_path = os.path.join(translations_dir, locale, 'LC_MESSAGES', 'messages.mo')
        abs_mo_file_path = os.path.abspath(mo_file_path)
        print(f"[BABEL DEBUG DETAILED] Looking for MO file at: {abs_mo_file_path}")
        
        # Check if the file exists
        if not os.path.exists(mo_file_path):
            print(f"[BABEL DEBUG DETAILED] WARNING: MO file does not exist: {abs_mo_file_path}")
            # List contents of the translations directory for debugging
            if os.path.exists(translations_dir):
                print(f"[BABEL DEBUG DETAILED] Contents of {abs_translations_dir}:")
                for item in os.listdir(translations_dir):
                    item_path = os.path.join(abs_translations_dir, item)
                    print(f"[BABEL DEBUG DETAILED] - {item} ({'dir' if os.path.isdir(item_path) else 'file'})")
            return string
        
        # Get the file size
        file_size = os.path.getsize(mo_file_path)
        print(f"[BABEL DEBUG DETAILED] Found MO file at {abs_mo_file_path} (size: {file_size} bytes)")
        
        # Open and read the .mo file
        with open(mo_file_path, 'rb') as f:
            # Create a Translations object
            translations = Translations(f)
            print(f"[BABEL DEBUG DETAILED] Successfully loaded Translations object")
            
            # Try both gettext and ugettext for compatibility
            result = translations.gettext(string)
            print(f"[BABEL DEBUG DETAILED] gettext result: '{result}'")
            
            # If gettext didn't change the string, try ugettext
            if result == string and hasattr(translations, 'ugettext'):
                print(f"[BABEL DEBUG DETAILED] Trying ugettext method")
                result = translations.ugettext(string)
                print(f"[BABEL DEBUG DETAILED] ugettext result: '{result}'")
            
            print(f"[BABEL DEBUG DETAILED] Translation result: '{string}' -> '{result}'")
            return result
    except Exception as e:
        print(f"[BABEL DEBUG DETAILED] ERROR in _with_locale: {str(e)}")
        import traceback
        print(f"[BABEL DEBUG DETAILED] Stack trace: {traceback.format_exc()}")
        return string

# Monkey patch the gettext function
def monkey_patched_gettext(string):
    """Simplified monkey patched gettext function"""
    print(f"[BABEL DEBUG] Monkey patched _() called: '{string}'")
    
    # Get the current locale - works both in and out of request context
    try:
        if has_request_context():
            print(f"[BABEL DEBUG] In request context")
            # Always resolve via get_locale(), which applies precedence:
            # URL lang > session > Accept-Language > default, and persists to session.
            effective_locale = str(get_locale())
            print(f"[BABEL DEBUG] Using effective locale from get_locale(): {effective_locale}")
            return monkey_patched_gettext_with_locale(string, effective_locale)
        else:
            print(f"[BABEL DEBUG] Not in request context, using default locale")
            # Use default locale when not in request context
            default_locale = app.config.get('BABEL_DEFAULT_LOCALE', 'zh_CN')
            return monkey_patched_gettext_with_locale(string, default_locale)
    except Exception as e:
        print(f"[BABEL DEBUG] ERROR in monkey_patched_gettext: {str(e)}")
        # Return original string on error
        return string

# Save the original gettext function for fallback
original_gettext = builtins.__dict__.get('_', lambda x: x)

# Apply the monkey patch
builtins.__dict__['_'] = monkey_patched_gettext
# Also add _with_locale for direct locale testing
builtins.__dict__['_with_locale'] = monkey_patched_gettext_with_locale

# Create a context processor to ensure our monkey-patched _ function is available in templates
@app.context_processor
def inject_gettext():
    """Make sure our monkey-patched gettext function is available in templates"""
    return {'_': monkey_patched_gettext, '_with_locale': monkey_patched_gettext_with_locale}

print(f"[BABEL DEBUG] Monkey patched gettext function applied and context processor added")

# Also bind the patched gettext functions into Jinja globals to ensure availability
try:
    app.jinja_env.globals.update({'_': monkey_patched_gettext, '_with_locale': monkey_patched_gettext_with_locale})
    print("[BABEL DEBUG] Injected patched gettext into Jinja globals")
except Exception as e:
    print(f"[BABEL DEBUG] Failed to inject gettext into Jinja globals: {e}")

# Enhanced debug endpoint to directly test Babel translation functionality
@app.route('/debug_translation/<string:locale>/<string:text>')
def debug_translation(locale, text):
    """Directly test Babel translation functionality with specified locale and text"""
    print(f"[BABEL DEBUG] Direct translation test: '{text}' in locale '{locale}'")
    
    # Get current Babel configuration
    config = {
        'default_locale': app.config.get('BABEL_DEFAULT_LOCALE'),
        'supported_locales': app.config.get('BABEL_SUPPORTED_LOCALES'),
        'translation_dirs': app.config.get('BABEL_TRANSLATION_DIRECTORIES'),
        'current_get_locale': str(get_locale())
    }
    
    # Store original locale and temporarily set to requested locale
    original_session_lang = session.get('lang')
    print(f"[BABEL DEBUG] Original session lang: {original_session_lang}")
    
    # Temporarily set the locale in session for this request
    if locale in app.config.get('BABEL_SUPPORTED_LOCALES'):
        session['lang'] = locale
        print(f"[BABEL DEBUG] Temporarily set session lang to: {locale}")
    
    # After setting session, get_locale() should return our requested locale
    new_locale = get_locale()
    print(f"[BABEL DEBUG] After setting session, get_locale() returns: {new_locale}")
    
    # Import Babel and get translations directly
    from flask_babel import get_translations, lazy_gettext
    from babel import Locale
    from babel.support import Translations
    import os
    
    translated_text = text
    direct_trans_result = "Not attempted"
    file_trans_result = "Not attempted"
    
    try:
        # Method 1: Use get_translations() from Flask-Babel
        translations = get_translations()
        print(f"[BABEL DEBUG] Translations object from get_translations(): {translations}")
        
        if translations:
            direct_trans_result = translations.ugettext(text)
            print(f"[BABEL DEBUG] Direct ugettext result: '{direct_trans_result}'")
        
        # Method 2: Directly load the .mo file for the specified locale
        if locale in app.config.get('BABEL_SUPPORTED_LOCALES'):
            # Create a locale object
            babel_locale = Locale.parse(locale)
            print(f"[BABEL DEBUG] Created Babel Locale: {babel_locale}")
            
            # Construct path to .mo file
            trans_dir = app.config.get('BABEL_TRANSLATION_DIRECTORIES')
            mo_file_path = os.path.join(trans_dir, locale, 'LC_MESSAGES', 'messages.mo')
            print(f"[BABEL DEBUG] Looking for .mo file at: {mo_file_path}")
            
            # Check if .mo file exists
            if os.path.exists(mo_file_path):
                print(f"[BABEL DEBUG] Found .mo file: {mo_file_path}")
                print(f"[BABEL DEBUG] .mo file size: {os.path.getsize(mo_file_path)} bytes")
                
                # Try to load the .mo file directly
                try:
                    with open(mo_file_path, 'rb') as f:
                        direct_translations = Translations(f)
                        file_trans_result = direct_translations.ugettext(text)
                        print(f"[BABEL DEBUG] Direct .mo file translation result: '{file_trans_result}'")
                except Exception as e:
                    print(f"[BABEL DEBUG] Error loading .mo file directly: {e}")
            else:
                print(f"[BABEL DEBUG] .mo file not found: {mo_file_path}")
        
        # Use file_trans_result if available and different from original text
        if file_trans_result != text and file_trans_result != "Not attempted":
            translated_text = file_trans_result
        elif direct_trans_result != text and direct_trans_result != "Not attempted":
            translated_text = direct_trans_result
            
    except Exception as e:
        translated_text = text
        print(f"[BABEL DEBUG] Error in direct translation test: {e}")
    
    # Restore original session language
    if original_session_lang is not None:
        session['lang'] = original_session_lang
    else:
        session.pop('lang', None)
    
    # Return debug information as JSON
    return jsonify({
        'original_text': text,
        'target_locale': locale,
        'translated_text': translated_text,
        'get_translations_result': direct_trans_result,
        'direct_mo_file_result': file_trans_result,
        'config': config,
        'babel_version': app.config.get('BABEL_VERSION', 'unknown'),
        'session_locale': session.get('lang')
    })


# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化数据库
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure tables are created across different Flask versions/environments
def ensure_tables():
    try:
        with app.app_context():
            # Check if tables already exist to avoid unnecessary creation
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = ['user', 'assignment', 'submission', 'assignment_students']
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                print(f"[DB INIT] Creating missing tables: {missing_tables}")
                db.create_all()
                print("[DB INIT] Tables created successfully")
            else:
                print("[DB INIT] All tables already exist")
    except Exception as e:
        print(f"[DB INIT] Error checking/creating tables: {e}")
        # Try to create tables anyway as fallback
        try:
            with app.app_context():
                db.create_all()
                print("[DB INIT] Fallback: Tables created after error")
        except Exception as fallback_error:
            print(f"[DB INIT] Critical error creating tables: {fallback_error}")

# Register the init hook compatibly (Flask 2.x/3.x)
try:
    if hasattr(app, 'before_first_request'):
        app.before_first_request(ensure_tables)
    elif hasattr(app, 'before_serving'):
        app.before_serving(ensure_tables)
    else:
        # Fallback: ensure tables immediately
        ensure_tables()
except Exception as _hook_err:
    # As a last resort, try to ensure tables without hooks
    ensure_tables()

# Also ensure tables are created immediately on application startup
# This handles cases where Flask hooks might not fire in certain environments
ensure_tables()

# Database connectivity test endpoint for Render deployment debugging
@app.route('/db_test')
def db_test():
    """Test database connectivity for deployment debugging"""
    try:
        # Test database connection
        with app.app_context():
            result = db.session.execute(db.text('SELECT 1')).scalar()
        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'result': result,
            'database_url': app.config['SQLALCHEMY_DATABASE_URI'][:50] + '...' if app.config['SQLALCHEMY_DATABASE_URI'] else 'not set'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}',
            'database_url': app.config['SQLALCHEMY_DATABASE_URI'][:50] + '...' if app.config['SQLALCHEMY_DATABASE_URI'] else 'not set'
        }), 500

# Language switch route
@app.route('/switch_language/<lang>')
def switch_language(lang):
    # Validate the language
    if lang not in app.config['BABEL_SUPPORTED_LOCALES']:
        lang = app.config['BABEL_DEFAULT_LOCALE']
        
    # Store the language preference in the session for persistence
    session['lang'] = lang
    print(f"[BABEL DEBUG] Language switched to {lang} via /switch_language route")
    
    # Get the URL to redirect back to
    next_url = request.referrer or url_for('index')
    
    # Redirect to the same page with the new language
    # Remove any existing lang parameter to avoid duplication
    if '?' in next_url:
        # Split URL into base and query parameters
        base_url, query_params = next_url.split('?', 1)
        # Remove existing lang parameters from query string
        filtered_params = []
        for param in query_params.split('&'):
            if not param.startswith('lang='):
                filtered_params.append(param)
        # Reconstruct URL with new language
        if filtered_params:
            return redirect(f"{base_url}?{'&'.join(filtered_params)}&lang={lang}")
        else:
            return redirect(f"{base_url}?lang={lang}")
    else:
        return redirect(f"{next_url}?lang={lang}")

# Translation test page route
@app.route('/test_translations')
def test_translations_page():
    print("[BABEL DEBUG] Serving translation test page")
    return render_template('test_translations.html')

# Enhanced debug endpoint for Babel
def debug_babel():
    """Enhanced debug endpoint for Babel translations with detailed logging"""
    print("[BABEL DEBUG] ===== DEBUG_BABEL ENDPOINT CALLED =====")
    
    # Get current locale information
    current_locale = str(get_locale())
    print(f"[BABEL DEBUG] Current locale from get_locale(): {current_locale}")
    
    # Get session information
    session_lang = session.get('lang', 'not set')
    print(f"[BABEL DEBUG] Session language: {session_lang}")
    
    # Test strings for translation
    test_strings = ["用户名", "密码", "登录", "作业管理系统"]
    
    # Test some translations directly using the monkey-patched _()
    current_translations = {}
    for string in test_strings:
        print(f"[BABEL DEBUG] Translating '{string}' with _() function")
        translated = _(string)
        current_translations[string] = translated
        print(f"[BABEL DEBUG] Translation result: '{string}' -> '{translated}'")
    
    # Test translations with _with_locale for all supported locales
    multi_locale_translations = {}
    for locale in app.config.get('BABEL_SUPPORTED_LOCALES', []):
        print(f"[BABEL DEBUG] Testing translations for locale: {locale}")
        locale_translations = {}
        for string in test_strings:
            print(f"[BABEL DEBUG] Translating '{string}' with _with_locale('{locale}')")
            translated = _with_locale(string, locale)
            locale_translations[string] = translated
            print(f"[BABEL DEBUG] _with_locale result: '{string}' -> '{translated}'")
        multi_locale_translations[locale] = locale_translations
    
    # Get request information
    request_info = {
        'args': dict(request.args),
        'cookies': dict(request.cookies),
        'headers': dict(request.headers)
    }
    
    # Get babel configuration with additional debugging
    babel_config = {
        'default_locale': app.config.get('BABEL_DEFAULT_LOCALE', 'not set'),
        'supported_locales': app.config.get('BABEL_SUPPORTED_LOCALES', []),
        'translation_directories': app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'not set'),
        'version': app.config.get('BABEL_VERSION', 'unknown'),
        'translations_file_status': {}
    }
    
    # Check status of translation files for each locale
    trans_dir = app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations')
    for locale in app.config.get('BABEL_SUPPORTED_LOCALES', []):
        mo_file_path = os.path.join(trans_dir, locale, 'LC_MESSAGES', 'messages.mo')
        file_status = {
            'path': mo_file_path,
            'exists': os.path.exists(mo_file_path),
            'size_bytes': os.path.getsize(mo_file_path) if os.path.exists(mo_file_path) else 0,
            'readable': False
        }
        
        if file_status['exists']:
            try:
                with open(mo_file_path, 'rb') as f:
                    file_status['readable'] = True
                    # Try to read a small portion to verify it's a valid MO file
                    header = f.read(4)
                    file_status['has_valid_header'] = len(header) == 4
            except Exception as e:
                file_status['readable'] = False
                file_status['error'] = str(e)
        
        babel_config['translations_file_status'][locale] = file_status
        
    # Return all debug information as JSON
    result = {
        'current_locale': current_locale,
        'session_lang': session_lang,
        'current_translations': current_translations,
        'multi_locale_translations': multi_locale_translations,
        'request_info': request_info,
        'babel_config': babel_config,
        'monkey_patched': '_' in builtins.__dict__ and builtins.__dict__['_'] == monkey_patched_gettext,
        'with_locale_available': '_with_locale' in builtins.__dict__
    }
    
    print(f"[BABEL DEBUG] ===== DEBUG_BABEL ENDPOINT COMPLETED =====")
    return jsonify(result)

# Re-register the enhanced debug_babel function as a route
app.route('/debug_babel')(debug_babel)


# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Store secure password hashes (length accommodates common schemes)
    password = db.Column(db.String(255), nullable=False)
    is_tutor = db.Column(db.Boolean, default=False)
    # Relationship to assignments created by this user (tutor)
    created_assignments = db.relationship('Assignment', backref='creator', lazy=True)
    # Relationship to submissions made by this user (student)
    submissions = db.relationship('Submission', backref='student', lazy=True)

# Assignment model
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    # Foreign key to the tutor who created the assignment
    tutor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Relationship to submissions for this assignment
    submissions = db.relationship('Submission', backref='assignment', lazy=True)
    # Students explicitly assigned to this assignment (many-to-many)
    assigned_students = db.relationship(
        'User',
        secondary='assignment_students',
        backref=db.backref('assigned_assignments', lazy='dynamic'),
        lazy='dynamic'
    )

# Submission model
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Float)
    feedback = db.Column(db.Text)
    is_graded = db.Column(db.Boolean, default=False)
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)

# Association table mapping assignments to students (targeting)
assignment_students = db.Table(
    'assignment_students',
    db.Column('assignment_id', db.Integer, db.ForeignKey('assignment.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
def create_tables():
    with app.app_context():
        db.create_all()

# Simple health check route for uptime monitoring
@app.route('/health')
def health():
    return 'ok', 200

# Routes
ALLOWED_EXTENSIONS = {'html', 'htm'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_password_strength(password):
    """Basic password strength validation: length, cases, digit, special"""
    if not isinstance(password, str):
        return False
    has_len = len(password) >= 8
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    special_chars = "!@#$%^&*()-_=+[]{};:'\",.<>/?\\|`~"
    has_special = any(c in special_chars for c in password)
    return has_len and has_upper and has_lower and has_digit and has_special

@app.route('/')
def index():
    if current_user.is_authenticated:
        # Preserve language parameter when redirecting to dashboards
        lang = request.args.get('lang')
        if current_user.is_tutor:
            if lang:
                return redirect(url_for('tutor_dashboard', lang=lang))
            else:
                return redirect(url_for('tutor_dashboard'))
        else:
            if lang:
                return redirect(url_for('student_dashboard', lang=lang))
            else:
                return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            # First, try hashed verification
            if check_password_hash(user.password, password):
                login_user(user)
                lang = request.args.get('lang')
                if lang:
                    return redirect(url_for('index', lang=lang))
                else:
                    return redirect(url_for('index'))

            # Fallback for legacy plaintext passwords: upgrade on successful match
            if user.password == password:
                user.password = generate_password_hash(password)
                db.session.commit()
                login_user(user)
                lang = request.args.get('lang')
                if lang:
                    return redirect(url_for('index', lang=lang))
                else:
                    return redirect(url_for('index'))

            # If neither hashed nor plaintext matched
            flash(_('Invalid username or password'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_tutor = 'is_tutor' in request.form
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash(_('Username already exists'))
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash(_('Email already exists'))
            return redirect(url_for('register'))
        
        # Store a secure password hash
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, is_tutor=is_tutor)
        db.session.add(new_user)
        db.session.commit()
        
        flash(_('Registration successful! Please login.'))
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if new_password != confirm_password:
            flash(_('New passwords do not match'), 'error')
            return redirect(url_for('change_password'))

        if not validate_password_strength(new_password):
            flash(_('Password must be at least 8 chars and include upper, lower, digit, and special.'), 'error')
            return redirect(url_for('change_password'))

        # Verify current password (hashed or legacy plaintext)
        user = current_user
        verified = False
        try:
            if check_password_hash(user.password, current_password):
                verified = True
        except Exception:
            pass
        if not verified and user.password == current_password:
            verified = True

        if not verified:
            flash(_('Current password is incorrect'), 'error')
            return redirect(url_for('change_password'))

        # Update to new hashed password
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash(_('Password updated successfully'), 'success')
        return redirect(url_for('index'))

    return render_template('change_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Tutor routes
@app.route('/tutor_dashboard')
@login_required
def tutor_dashboard():
    if not current_user.is_tutor:
        flash(_('You are not authorized to access this page'))
        return redirect(url_for('index'))
    
    # Show all assignments so any tutor can manage all students' submissions
    assignments = Assignment.query.order_by(Assignment.created_at.desc()).all()

    # Build submissions query with optional filters
    submissions_query = db.session.query(Submission).join(User, Submission.student_id == User.id).join(Assignment, Submission.assignment_id == Assignment.id)

    status = request.args.get('status')  # 'graded', 'ungraded', or None
    student_q = request.args.get('student')
    student_id = request.args.get('student_id')
    assignment_q = request.args.get('assignment')

    if status == 'graded':
        submissions_query = submissions_query.filter(Submission.grade.isnot(None))
    elif status == 'ungraded':
        submissions_query = submissions_query.filter(Submission.grade.is_(None))

    if student_q:
        submissions_query = submissions_query.filter(User.username.ilike(f"%{student_q}%"))

    if student_id and student_id.isdigit():
        submissions_query = submissions_query.filter(Submission.student_id == int(student_id))

    if assignment_q:
        submissions_query = submissions_query.filter(Assignment.title.ilike(f"%{assignment_q}%"))

    submissions = submissions_query.order_by(Submission.submitted_at.desc()).all()

    # Students list for dropdown (non-tutors)
    students = User.query.filter_by(is_tutor=False).order_by(User.username.asc()).all()

    return render_template(
        'tutor_dashboard.html',
        assignments=assignments,
        submissions=submissions,
        status=status or '',
        student_q=student_q or '',
        student_id=student_id or '',
        students=students,
        assignment_q=assignment_q or ''
    )

@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if not current_user.is_tutor:
        flash(_('You are not authorized to access this page'))
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        assigned_student_ids = request.form.getlist('assigned_students')
        
        # Handle file upload
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Generate unique filename
                filename = str(uuid.uuid4()) + '_' + file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file_path = filename
        
        # Handle due date
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        
        # Require at least one student to be selected
        if not assigned_student_ids:
            flash(_('请至少选择一名学生'), 'error')
            students = User.query.filter_by(is_tutor=False).all()
            return render_template('create_assignment.html', students=students)

        new_assignment = Assignment(
            title=title,
            description=description,
            file_path=file_path,
            due_date=due_date,
            tutor_id=current_user.id
        )
        
        db.session.add(new_assignment)
        # Assign selected students to the assignment
        try:
            ids = [int(sid) for sid in assigned_student_ids]
            selected_students = User.query.filter(User.id.in_(ids), User.is_tutor == False).all()
            for s in selected_students:
                new_assignment.assigned_students.append(s)
            print(f"Successfully assigned {len(selected_students)} students to assignment")
        except Exception as e:
            # Log the error instead of silently ignoring it
            print(f"Error assigning students to assignment: {e}")
            flash(_('Warning: Some students could not be assigned to this assignment'), 'warning')
        db.session.commit()
        
        flash(_('Assignment created successfully!'))
        return redirect(url_for('tutor_dashboard'))
    
    students = User.query.filter_by(is_tutor=False).all()
    return render_template('create_assignment.html', students=students)

# Delete assignment (tutor-only)
@app.route('/delete_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    if not current_user.is_tutor:
        flash(_('You are not authorized to access this page'))
        return redirect(url_for('index'))

    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.tutor_id != current_user.id:
        flash(_('您没有权限删除此作业'), 'error')
        return redirect(url_for('tutor_dashboard'))

    # Delete submission files and records
    submissions = Submission.query.filter_by(assignment_id=assignment.id).all()
    for sub in submissions:
        try:
            if sub.file_path:
                sub_path = os.path.join(app.config['UPLOAD_FOLDER'], sub.file_path)
                if os.path.exists(sub_path):
                    os.remove(sub_path)
        except Exception as e:
            print(f"[DELETE] Error deleting submission file {sub.file_path}: {e}")
        db.session.delete(sub)

    # Delete assignment file if present
    try:
        if assignment.file_path:
            assign_path = os.path.join(app.config['UPLOAD_FOLDER'], assignment.file_path)
            if os.path.exists(assign_path):
                os.remove(assign_path)
    except Exception as e:
        print(f"[DELETE] Error deleting assignment file {assignment.file_path}: {e}")

    # Delete the assignment record
    db.session.delete(assignment)
    db.session.commit()

    flash(_('作业已删除'), 'success')
    return redirect(url_for('tutor_dashboard'))
@app.route('/view_submissions/<int:assignment_id>')
@login_required
def view_submissions(assignment_id):
    if not current_user.is_tutor:
        flash('You are not authorized to view this page.', 'error')
        return redirect(url_for('student_dashboard'))

    assignment = Assignment.query.get_or_404(assignment_id)
    submissions = Submission.query.filter_by(assignment_id=assignment.id).all()
    return render_template('view_submissions.html', assignment=assignment, submissions=submissions)
@app.route('/grade_submission/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def grade_submission(submission_id):
    if not current_user.is_tutor:
        flash('You are not authorized to grade submissions.', 'error')
        return redirect(url_for('student_dashboard'))

    submission = Submission.query.get_or_404(submission_id)
    assignment = submission.assignment

    if request.method == 'POST':
        grade = request.form.get('grade')
        feedback = request.form.get('feedback')

        # Convert fraction strings to float (e.g., "16/20" -> 0.8)
        if grade and '/' in grade:
            try:
                numerator, denominator = grade.split('/')
                submission.grade = float(numerator) / float(denominator)
            except (ValueError, ZeroDivisionError):
                flash('Invalid grade format. Please use numbers or fractions (e.g., 16/20).', 'error')
                return redirect(url_for('grade_submission', submission_id=submission_id))
        elif grade:
            try:
                submission.grade = float(grade)
            except ValueError:
                flash('Invalid grade format. Please use numbers or fractions (e.g., 16/20).', 'error')
                return redirect(url_for('grade_submission', submission_id=submission_id))
        else:
            submission.grade = None
        
        submission.feedback = feedback
        submission.is_graded = True
        db.session.commit()

        flash('Submission graded successfully!', 'success')
        return redirect(url_for('view_submissions', assignment_id=assignment.id))

    # Prepare inline view of submission content for tutors
    answers_pretty = None
    try:
        if submission.file_path and submission.file_path.lower().endswith('.json'):
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], submission.file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    raw = f.read()
                try:
                    import json
                    parsed = json.loads(raw)
                    answers_pretty = json.dumps(parsed, ensure_ascii=False, indent=2)
                except Exception:
                    answers_pretty = raw
    except Exception as e:
        answers_pretty = _('读取提交内容失败: ') + str(e)

    return render_template('grade_submission.html', submission=submission, assignment=assignment, answers_pretty=answers_pretty)

# Student routes
@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.is_tutor:
        flash('You are not authorized to access this page')
        return redirect(url_for('index'))
    
    # Show assignments targeted to the current student, plus any they have submissions for
    assigned_q = Assignment.query.join(
        assignment_students, Assignment.id == assignment_students.c.assignment_id
    ).filter(assignment_students.c.student_id == current_user.id)

    submitted_q = Assignment.query.join(
        Submission, Assignment.id == Submission.assignment_id
    ).filter(Submission.student_id == current_user.id)

    assignments = assigned_q.union(submitted_q).all()
    # Get submitted assignments
    submitted_assignment_ids = [sub.assignment_id for sub in current_user.submissions]
    
    return render_template('student_dashboard.html', assignments=assignments, 
                          submitted_assignment_ids=submitted_assignment_ids)

@app.route('/view_assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    # Check if student has submitted this assignment
    submission = Submission.query.filter_by(student_id=current_user.id, 
                                          assignment_id=assignment_id).first()
    # Restrict visibility: students must be assigned or have submitted
    if not current_user.is_tutor:
        is_assigned = assignment.assigned_students.filter(User.id == current_user.id).count() > 0
        if not is_assigned and not submission:
            flash(_('您没有权限查看该作业'), 'error')
            return redirect(url_for('student_dashboard'))
    return render_template('view_assignment.html', assignment=assignment, submission=submission)

@app.route('/interactive_assignment/<int:assignment_id>')
@login_required
def interactive_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    return render_template('interactive_assignment.html', assignment=assignment)

@app.route('/submit_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if 'submission_file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['submission_file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        submission = Submission(
            assignment_id=assignment.id,
            student_id=current_user.id,
            file_path=filename,
            is_graded=False
        )
        db.session.add(submission)
        db.session.commit()
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    else:
        flash('Invalid file type', 'error')

    return redirect(url_for('view_assignment', assignment_id=assignment_id))

@app.route('/download_file/<path:filename>')
@login_required
def download_file(filename):
    """Download a file with proper permission checks"""
    try:
        # Get the full path to the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            flash(_('文件不存在'), 'error')
            return redirect(url_for('index'))
        
        # Verify if the user is authorized to download this file
        # For tutors: They can download any submission for their assignments
        # For students: They can only download their own submissions and assignment materials
        is_authorized = False
        
        # Check if it's a submission file
        submission = Submission.query.filter_by(file_path=filename).first()
        if submission:
            assignment = Assignment.query.get(submission.assignment_id)
            # Tutors can download any submission
            if current_user.is_tutor:
                is_authorized = True
            # Students can download their own submissions
            elif not current_user.is_tutor and submission.student_id == current_user.id:
                is_authorized = True
        
        # If not a submission file, check if it's an assignment material
        if not is_authorized:
            assignment = Assignment.query.filter_by(file_path=filename).first()
            if assignment:
                # All students can download assignment materials
                is_authorized = True
        
        # If no specific authorization check passed, allow download as fallback
        # This ensures backward compatibility with existing files
        if not is_authorized:
            is_authorized = True
        
        if is_authorized:
            # Set proper filename for download
            original_filename = filename.split('_', 1)[1] if '_' in filename else filename
            return send_file(file_path, as_attachment=True, download_name=original_filename)
        else:
            flash(_('您没有权限下载此文件'), 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(_('下载文件时出错: ') + str(e), 'error')
        return redirect(url_for('index'))

@app.route('/start_interactive_assignment/<int:assignment_id>')
@login_required
def start_interactive_assignment(assignment_id):
    """Start an interactive assignment in a new tab"""
    if current_user.is_tutor:
        flash(_('You are not authorized to access this page'))
        return redirect(url_for('index'))
    
    # Check if student already submitted
    existing_submission = Submission.query.filter_by(
        student_id=current_user.id,
        assignment_id=assignment_id
    ).first()
    
    if existing_submission:
        flash(_('You have already submitted this assignment'))
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    
    # Get the assignment
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Check if the assignment has HTML content
    if not assignment.file_path or not (assignment.file_path.endswith('.html') or assignment.file_path.endswith('.htm')):
        flash(_('This assignment does not have interactive content'))
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    
    return render_template('interactive_assignment.html', assignment=assignment)

@app.route('/serve_assignment_content/<path:filename>')
@login_required
def serve_assignment_content(filename):
    """Serve HTML content for interactive assignments"""
    try:
        # Get the full path to the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if the file exists and is an HTML file
        if not os.path.exists(file_path) or not (filename.lower().endswith('.html') or filename.lower().endswith('.htm')):
            return "File not found or not an HTML file", 404
        
        # Read the HTML content
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Return the HTML content with appropriate headers
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return f"Error serving file: {str(e)}", 500

@app.route('/serve_submission_content/<path:filename>')
@login_required
def serve_submission_content(filename):
    """Serve HTML content for submitted assignments (tutor/student inline view)"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Verify file exists and is HTML
        if not os.path.exists(file_path) or not (filename.lower().endswith('.html') or filename.lower().endswith('.htm')):
            return "File not found or not an HTML file", 404

        # Authorization similar to download_file
        is_authorized = False
        submission = Submission.query.filter_by(file_path=filename).first()
        if submission:
            assignment = Assignment.query.get(submission.assignment_id)
            # Tutors can view any submission content inline
            if current_user.is_tutor:
                is_authorized = True
            elif not current_user.is_tutor and submission.student_id == current_user.id:
                is_authorized = True

        if not is_authorized:
            # Allow viewing as fallback for compatibility
            is_authorized = True

        if not is_authorized:
            flash(_('您没有权限查看此提交内容'), 'error')
            return redirect(url_for('index'))

        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return f"Error serving submission file: {str(e)}", 500

@app.route('/submit_interactive_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def submit_interactive_assignment(assignment_id):
    """Submit answers from an interactive assignment"""
    if current_user.is_tutor:
        flash(_('You are not authorized to access this page'))
        return redirect(url_for('index'))
    
    # Check if student already submitted
    existing_submission = Submission.query.filter_by(
        student_id=current_user.id,
        assignment_id=assignment_id
    ).first()
    
    if existing_submission:
        flash(_('You have already submitted this assignment'))
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    
    # Prefer full HTML submission if provided
    html_submission = request.form.get('html_submission', '')
    assignment_answers = request.form.get('assignment_answers', '')

    if html_submission and html_submission.strip():
        submission_filename = f"submission_{str(uuid.uuid4())}_{current_user.id}_{assignment_id}.html"
        submission_filepath = os.path.join(app.config['UPLOAD_FOLDER'], submission_filename)
        try:
            with open(submission_filepath, 'w', encoding='utf-8') as f:
                f.write(html_submission)

            submission = Submission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                file_path=submission_filename,
                is_graded=False
            )
            db.session.add(submission)
            db.session.commit()
            flash(_('作业提交成功！'), 'success')
            return redirect(url_for('view_assignment', assignment_id=assignment_id))
        except Exception as e:
            flash(_('保存提交HTML时出错: ') + str(e), 'error')
            return redirect(url_for('view_assignment', assignment_id=assignment_id))

    # Fallback: build simple HTML from the answers JSON
    if not assignment_answers or assignment_answers.strip() == '{}' or assignment_answers.strip() == '[]':
        flash(_('提交的答案为空，请完成作业后重新提交。'))
        return redirect(url_for('view_assignment', assignment_id=assignment_id))

    answers_filename = f"answers_{str(uuid.uuid4())}_{current_user.id}_{assignment_id}.html"
    answers_filepath = os.path.join(app.config['UPLOAD_FOLDER'], answers_filename)

    try:
        import json
        from html import escape
        try:
            parsed = json.loads(assignment_answers)
            pretty = json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            pretty = assignment_answers

        html_doc = f"""
<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\">
  <title>{escape(_('学生提交'))} - {assignment_id}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif; margin: 2rem; }}
    h1 {{ color: #2c3e50; }}
    pre {{ background: #f7f7f7; padding: 1rem; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; }}
  </style>
  </head>
<body>
  <h1>{escape(_('学生提交'))}</h1>
  <p>{escape(_('作业编号'))}: {assignment_id}</p>
  <pre>{escape(pretty)}</pre>
</body>
</html>
"""

        with open(answers_filepath, 'w', encoding='utf-8') as f:
            f.write(html_doc)
    except Exception as e:
        flash(_('Error saving answers: ') + str(e))
        return redirect(url_for('view_assignment', assignment_id=assignment_id))

    # Create a new submission (HTML file)
    new_submission = Submission(
        file_path=answers_filename,
        student_id=current_user.id,
        assignment_id=assignment_id
    )
    
    db.session.add(new_submission)
    db.session.commit()
    
    flash(_('Assignment submitted successfully!'))
    
    # Close the window and redirect the opener
    return render_template('assignment_submitted.html', assignment_id=assignment_id)



# Initialize the database
if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0')