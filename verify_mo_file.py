import os
import gettext

# Function to verify the content of a .mo file
def verify_mo_file(locale_code):
    print(f"\n===== Verifying {locale_code} .mo file ======")
    
    # Path to the .mo file
    translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
    mo_file_path = os.path.join(translations_dir, locale_code, 'LC_MESSAGES', 'messages.mo')
    
    print(f"Checking .mo file at: {mo_file_path}")
    
    # Check if the file exists
    if not os.path.exists(mo_file_path):
        print(f"Error: .mo file not found for {locale_code}")
        return False
    
    # Check if the file is readable
    if not os.access(mo_file_path, os.R_OK):
        print(f"Error: .mo file exists but is not readable for {locale_code}")
        return False
    
    print(f".mo file size: {os.path.getsize(mo_file_path)} bytes")
    
    try:
        # Try to load the .mo file using gettext
        translation = gettext.GNUTranslations(open(mo_file_path, 'rb'))
        
        # Define test phrases
        test_phrases = [
            "作业管理系统",
            "登录",
            "用户登录",
            "用户名",
            "密码"
        ]
        
        print(f"\nTesting translations from {locale_code} .mo file:")
        
        # Test each phrase
        all_translations_found = True
        for phrase in test_phrases:
            translated = translation.gettext(phrase)
            print(f"- '{phrase}' -> '{translated}'")
            
            # For Traditional Chinese, check if it contains Traditional characters
            if locale_code == 'zh_TW':
                if '作業' not in translated and '登錄' not in translated and '用戶' not in translated:
                    print(f"  ✗ Warning: '{translated}' doesn't appear to be Traditional Chinese")
                    all_translations_found = False
            
            # For English, check if it's translated to English
            elif locale_code == 'en' and translated == phrase:
                print(f"  ✗ Warning: '{phrase}' is not translated to English")
                all_translations_found = False
        
        return all_translations_found
        
    except Exception as e:
        print(f"Error loading or using .mo file: {e}")
        return False

# Function to recompile a specific .po file
def recompile_po_file(locale_code):
    print(f"\n===== Recompiling {locale_code} .po file ======")
    
    # Paths
    translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
    po_file_path = os.path.join(translations_dir, locale_code, 'LC_MESSAGES', 'messages.po')
    mo_file_path = os.path.join(translations_dir, locale_code, 'LC_MESSAGES', 'messages.mo')
    
    print(f"PO file: {po_file_path}")
    print(f"MO file destination: {mo_file_path}")
    
    # Check if PO file exists
    if not os.path.exists(po_file_path):
        print(f"Error: .po file not found for {locale_code}")
        return False
    
    try:
        # Use gettext to compile the PO file to MO
        print("Compiling PO to MO...")
        
        # Read the PO file
        with open(po_file_path, 'rb') as f:
            po_content = f.read()
        
        # Compile to MO
        from babel.messages.pofile import read_po
        from babel.messages.mofile import write_mo
        
        # Parse the PO file
        catalog = read_po(open(po_file_path, 'r', encoding='utf-8'))
        
        # Write the MO file
        with open(mo_file_path, 'wb') as f:
            write_mo(f, catalog)
        
        print(f"Successfully recompiled {locale_code} .po file to .mo")
        print(f"New .mo file size: {os.path.getsize(mo_file_path)} bytes")
        return True
        
    except ImportError:
        print("Error: Babel library not available. Please install it with 'pip install babel'")
        return False
    except Exception as e:
        print(f"Error recompiling .po file: {e}")
        return False

# Main function
def main():
    print("=== MO File Verification Tool ===")
    
    # First verify all MO files
    locales = ['zh_CN', 'zh_TW', 'en']
    
    for locale in locales:
        verify_mo_file(locale)
    
    # Special focus on zh_TW - recompile if needed
    print("\n=== Special attention to Traditional Chinese ===")
    
    # Check if we need to install Babel first
    try:
        import babel
        print(f"Babel version {babel.__version__} is installed")
        
        # Ask if user wants to recompile zh_TW
        print("\nDo you want to force-recompile the Traditional Chinese (zh_TW) .po file?")
        print("This can fix issues with corrupted .mo files.")
        print("(The script will automatically recompile without user input)")
        
        # Recompile zh_TW
        recompile_po_file('zh_TW')
        
        # Verify again after recompilation
        print("\nVerifying recompiled zh_TW .mo file:")
        verify_mo_file('zh_TW')
        
    except ImportError:
        print("\nBabel library not installed. Please run 'pip install babel' and try again.")
    
    print("\n=== MO File Verification Completed ===")
    print("If Traditional Chinese translations still aren't working after verification and recompilation,")
    print("try the following:")
    print("1. Check that the .po file contains the correct msgid/msgstr pairs")
    print("2. Make sure Flask-Babel is correctly configured to use the translations directory")
    print("3. Try restarting the Flask server")
    print("4. Check for any errors in the Flask server logs related to translation loading")

if __name__ == "__main__":
    main()