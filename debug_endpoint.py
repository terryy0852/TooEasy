
from flask import Flask, request, jsonify, session
from flask_babel import get_locale, gettext as _

# Assuming app and babel are already initialized

@app.route('/debug_babel')
def debug_babel():
    # Get current locale information
    current_locale = str(get_locale())
    
    # Get session information
    session_lang = session.get('lang', 'not set')
    
    # Test some translations directly
    translations = {
        '作业管理系统': _('作业管理系统'),
        '登录': _('登录'),
        '用户登录': _('用户登录'),
        '用户名': _('用户名'),
        '密码': _('密码')
    }
    
    # Get request information
    request_info = {
        'args': dict(request.args),
        'cookies': dict(request.cookies),
        'headers': dict(request.headers)
    }
    
    # Get babel configuration
    babel_config = {
        'default_locale': app.config.get('BABEL_DEFAULT_LOCALE', 'not set'),
        'supported_locales': app.config.get('BABEL_SUPPORTED_LOCALES', []),
        'translation_directories': app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'not set')
    }
    
    # Return all debug information as JSON
    return jsonify({
        'current_locale': current_locale,
        'session_lang': session_lang,
        'translations': translations,
        'request_info': request_info,
        'babel_config': babel_config
    })
