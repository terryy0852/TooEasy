import sys
import os
from app import app

# Change to the project directory
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"[📁] Changed to directory: {os.getcwd()}")
except Exception as e:
    print(f"[❌] Error changing directory: {e}")

# Start server on a different port
try:
    print("[🚀] Starting server on alternative port 8080...")
    app.run(
        host='127.0.0.1',  # Use localhost instead of 0.0.0.0 for better compatibility
        port=8080,
        debug=False,
        use_reloader=False  # Disable reloader to avoid environment issues
    )
except Exception as e:
    print(f"[❌] Server startup error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)