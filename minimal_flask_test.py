from flask import Flask

# Create the simplest possible Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello Flask!'

@app.route('/login')
def login():
    return 'Login Page'

if __name__ == '__main__':
    print("[📦] Starting minimal Flask app...")
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=False
        )
    except Exception as e:
        print(f"[❌] Flask startup error: {e}")
        import traceback
        traceback.print_exc()