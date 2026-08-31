import os
import io
import polib

def compile_po_to_mo(po_file_path, mo_file_path):
    try:
        # Read the PO file
        po = polib.pofile(po_file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(mo_file_path), exist_ok=True)
        
        # Write the MO file
        po.save_as_mofile(mo_file_path)
        print(f"Successfully compiled {po_file_path} to {mo_file_path}")
        return True
    except Exception as e:
        print(f"Error compiling {po_file_path}: {str(e)}")
        return False

if __name__ == "__main__":
    # Compile Simplified Chinese translations
    zh_cn_po = "translations/zh_CN/LC_MESSAGES/messages.po"
    zh_cn_mo = "translations/zh_CN/LC_MESSAGES/messages.mo"
    compile_po_to_mo(zh_cn_po, zh_cn_mo)
    
    # Compile English translations
    en_po = "translations/en/LC_MESSAGES/messages.po"
    en_mo = "translations/en/LC_MESSAGES/messages.mo"
    compile_po_to_mo(en_po, en_mo)
    
    # Compile Traditional Chinese translations
    zh_tw_po = "translations/zh_TW/LC_MESSAGES/messages.po"
    zh_tw_mo = "translations/zh_TW/LC_MESSAGES/messages.mo"
    compile_po_to_mo(zh_tw_po, zh_tw_mo)