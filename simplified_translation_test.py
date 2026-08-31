#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simplified test script to directly test the monkey-patched _() function
with different locales and capture detailed debug output.
"""

import os
import sys
import logging
from flask import Flask, session
from flask_babel import Babel
import builtins
import threading
import functools

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Create a minimal Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# Initialize Babel
babel = Babel(app)

# Define the locale selector function
def get_locale():
    """Get the current locale from session or use default."""
    print("[BABEL DEBUG] ===== Locale Selection Process Started =====")
    print(f"[BABEL DEBUG] Session data: {session}")
    
    # Get language from session if available
    lang = session.get('lang')
    if lang:
        print(f"[BABEL DEBUG] Found language in session: {lang}")
    
    # Fallback to default locale if no language is found
    if not lang or lang not in app.config['BABEL_SUPPORTED_LOCALES']:
        old_lang = lang
        lang = app.config['BABEL_DEFAULT_LOCALE']
        print(f"[BABEL DEBUG] Language {old_lang} not valid or not supported, falling back to default: {lang}")
    else:
        print(f"[BABEL DEBUG] Selected valid language: {lang}")
    
    print(f"[BABEL DEBUG] Final selected locale: {lang}")
    print("[BABEL DEBUG] ===== Locale Selection Process Completed =====")
    
    return lang

# Register the locale selector with Babel - adapting for different Flask-Babel versions
try:
    # Try newer API
    @babel.localeselector
    def select_locale():
        return get_locale()
    print("[BABEL DEBUG] Registered locale selector using decorator API")
except AttributeError:
    # Fall back to older API
    try:
        babel.init_app(app, locale_selector=get_locale)
        print("[BABEL DEBUG] Registered locale selector using init_app API")
    except Exception as e:
        print(f"[BABEL DEBUG] Error registering locale selector: {e}")

# Function to load translations directly from .mo files
def get_translation_from_file(message, locale):
    """Load translation directly from .mo files with detailed debugging."""
    print(f"[BABEL DEBUG] get_translation_from_file called with '{message}' and locale '{locale}'")
    
    try:
        # Construct the path to the .mo file
        translations_dir = app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations')
        mo_file_path = os.path.join(
            translations_dir,
            locale,
            'LC_MESSAGES',
            'messages.mo'
        )
        print(f"[BABEL DEBUG] Looking for .mo file at: {mo_file_path}")
        
        # Check if the directory exists
        mo_dir = os.path.dirname(mo_file_path)
        dir_exists = os.path.isdir(mo_dir)
        print(f"[BABEL DEBUG] Directory exists: {dir_exists}")
        
        # Check if the .mo file exists
        if not os.path.exists(mo_file_path):
            print(f"[BABEL DEBUG] .mo file not found: {mo_file_path}")
            return message
        
        print(f"[BABEL DEBUG] Found .mo file: {mo_file_path}")
        
        # Check file size
        file_size = os.path.getsize(mo_file_path)
        print(f"[BABEL DEBUG] File size: {file_size} bytes")
        
        if file_size == 0:
            print(f"[BABEL DEBUG] .mo file is empty: {mo_file_path}")
            return message
        
        # Try to open the .mo file
        try:
            from babel.support import Translations
            from babel.messages.mofile import read_mo
            with open(mo_file_path, 'rb') as f:
                print("[BABEL DEBUG] Successfully opened .mo file")
                
                # Try to read the mo file directly for debugging
                try:
                    catalog = read_mo(f)
                    print(f"[BABEL DEBUG] Successfully read MO catalog")
                    print(f"[BABEL DEBUG] Catalog contains {len(catalog)} messages")
                    print(f"[BABEL DEBUG] Catalog domains: {catalog.domain}")
                    # Try to check if our specific message is in the catalog
                    if message in catalog:
                        print(f"[BABEL DEBUG] Message '{message}' is in the catalog!")
                        catalog_result = catalog[message]
                        print(f"[BABEL DEBUG] Catalog translation: '{message}' -> '{catalog_result}'")
                    else:
                        print(f"[BABEL DEBUG] Message '{message}' is NOT in the catalog")
                        # Print some sample messages from the catalog for debugging
                        if len(catalog) > 0:
                            sample_messages = list(catalog.items())[:3]
                            print(f"[BABEL DEBUG] Sample messages in catalog: {sample_messages}")
                except Exception as e:
                    print(f"[BABEL DEBUG] Error reading MO catalog directly: {e}")
                
                # Reset file cursor for Translations object
                f.seek(0)
                
                # Create Translations object without locale parameter
                translations = Translations(f)
                print("[BABEL DEBUG] Successfully created Translations object")
                print(f"[BABEL DEBUG] Translations object type: {type(translations)}")
                print(f"[BABEL DEBUG] Translations object attributes: {dir(translations)}")
                
                # Try to translate the message using gettext
                result = translations.gettext(message)
                print(f"[BABEL DEBUG] gettext result: '{message}' -> '{result}'")
                
                # Also try with ugettext for Python 2 compatibility
                try:
                    if hasattr(translations, 'ugettext'):
                        u_result = translations.ugettext(message)
                        print(f"[BABEL DEBUG] ugettext result: '{message}' -> '{u_result}'")
                except Exception as e:
                    print(f"[BABEL DEBUG] Error with ugettext: {e}")
                
                # Try with gettext method directly
                try:
                    direct_result = Translations(f).gettext(message)
                    print(f"[BABEL DEBUG] Direct gettext result: '{message}' -> '{direct_result}'")
                except Exception as e:
                    print(f"[BABEL DEBUG] Error with direct gettext: {e}")
                    
                return result
        except ImportError:
            print("[BABEL DEBUG] babel module not found")
        except Exception as e:
            print(f"[BABEL DEBUG] Error loading .mo file: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"[BABEL DEBUG] Unexpected error in get_translation_from_file: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # If all else fails, return the original message
    print(f"[BABEL DEBUG] Returning original message: '{message}'")
    return message

# Create a monkey-patched version of gettext that uses our file-based translation
# with enhanced debugging
@functools.lru_cache(maxsize=128)
def monkey_patched_gettext(message):
    """Monkey-patched version of gettext that uses our file-based translation."""
    print("[BABEL DEBUG] ===== Translation Attempt Started =====")
    print(f"[BABEL DEBUG] Translation called for message: '{message}'")
    print(f"[BABEL DEBUG] Current thread: {threading.current_thread().name}")
    
    try:
        # Get the current locale
        locale = get_locale()
        print(f"[BABEL DEBUG] Current locale from get_locale(): {locale}")
        
        # Log session data if available
        try:
            print(f"[BABEL DEBUG] Session data in translation: {session}")
        except Exception as e:
            print(f"[BABEL DEBUG] Error accessing session: {e}")
        
        # Log Babel configuration
        print(f"[BABEL DEBUG] Babel translation directory: {app.config.get('BABEL_TRANSLATION_DIRECTORIES')}")
        print(f"[BABEL DEBUG] Babel supported locales: {app.config.get('BABEL_SUPPORTED_LOCALES')}")
        
        # Use our custom translation function
        print(f"[BABEL DEBUG] Calling get_translation_from_file with message='{message}', locale='{locale}'")
        result = get_translation_from_file(message, locale)
        print(f"[BABEL DEBUG] Translation result: '{message}' -> '{result}'")
        
        print("[BABEL DEBUG] ===== Translation Attempt Completed =====")
        return result
    except Exception as e:
        print(f"[BABEL DEBUG] Error in monkey_patched_gettext: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print("[BABEL DEBUG] ===== Translation Attempt Failed =====")
        return message

# Monkey patch the _() function in builtins
builtins.__dict__['_'] = monkey_patched_gettext
print("[BABEL DEBUG] Monkey-patching of _() function completed")

# Function to test translations with different locales
def test_translations():
    """Test translations with different locales and print results."""
    test_messages = ["用户名", "密码", "登录", "作业管理系统"]
    test_locales = ["zh_CN", "zh_TW", "en"]
    
    print("\n===== STARTING TRANSLATION TEST =====\n")
    
    # Create a test request context
    with app.test_request_context('/'):
        # Set up the session
        app.preprocess_request()
        
        for locale in test_locales:
            print(f"\n=== Testing with locale: {locale} ===")
            
            # Set the locale in the session
            session['lang'] = locale
            print(f"[TEST] Set session language to: {locale}")
            
            # Test each message
            for message in test_messages:
                print(f"\n[TEST] Translating: '{message}'")
                result = _(message)  # Use the monkey-patched _() function
                print(f"[TEST] Result: '{result}'")
                
    print("\n===== TEST COMPLETED =====")

# Run the test
if __name__ == "__main__":
    print("[TEST] Starting simplified translation test...")
    test_translations()