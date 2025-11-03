#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the _with_locale function that accepts explicit locale parameters
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_separator(title):
    """Print a decorative separator with title"""
    print("\n" + "="*60)
    print(f"{title.center(60)}")
    print("="*60)

def test_with_locale():
    """Test the _with_locale function with different locales"""
    print_separator("TESTING _with_locale FUNCTION")
    
    # Import the app and _with_locale function
    from app import app
    
    # The _with_locale function should be available in builtins
    import builtins
    if not hasattr(builtins, '_with_locale'):
        print("Error: _with_locale function not found in builtins!")
        return
    
    _with_locale = builtins._with_locale
    
    # Test phrases
    phrases = ['用户名', '密码', '登录', '作业管理系统']
    
    # Test with different locales
    locales = [('zh_CN', 'Simplified Chinese'), ('zh_TW', 'Traditional Chinese'), ('en', 'English')]
    
    for locale_name, display_name in locales:
        print(f"\nTesting with explicit locale: {display_name} ({locale_name})")
        
        for phrase in phrases:
            try:
                translated = _with_locale(phrase, locale_name)
                print(f"  '{phrase}' -> '{translated}'")
            except Exception as e:
                print(f"  Error translating '{phrase}': {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    print("Starting _with_locale tests...")
    
    try:
        # Import the app first
        from app import app
        
        # Configure the app for testing
        app.config['TESTING'] = True
        
        # Run the test
        test_with_locale()
        
        print("\n_with_locale Test Complete!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()