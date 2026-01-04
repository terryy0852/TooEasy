# Minimal test server to isolate the BuildError issue
from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = 'test_secret_key'

# Minimal password reset routes
@app.route('/login')
def login():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Login</h1>
            <form action="{{ url_for('login') }}" method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <div style="margin-top: 15px; text-align: center;">
                <a href="{{ url_for('forgot_password') }}">Forgot Password?</a>
            </div>
        </body>
        </html>
    ''')

@app.route('/forgot_password')
def forgot_password():
    return "Forgot Password Page"

@app.route('/reset_password/<token>')
def reset_password(token):
    return f"Reset Password Page (Token: {token})"

if __name__ == '__main__':
    print("Starting minimal test server on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)
