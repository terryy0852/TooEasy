import fileinput
import re

# Read the app.py file with UTF-8 encoding
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the password reset routes to add
reset_routes = '''
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash(_('Please enter your email address'), 'error')
            return redirect(url_for('forgot_password'))
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token and expiry
            reset_token = str(uuid.uuid4())
            reset_token_expiry = datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour
            
            # Update user with reset token
            user.reset_token = reset_token
            user.reset_token_expiry = reset_token_expiry
            db.session.commit()
            
            # Since there's no email system configured, we'll show the token
            # In a real system, you would send this link via email
            flash(_('Password reset token generated. Copy this token:'), 'info')
            flash(f'Token: {reset_token}', 'info')
            flash(_('Use this link to reset your password:'), 'info')
            flash(f'{url_for("reset_password", token=reset_token, _external=True)}', 'info')
            
        else:
            flash(_('If an account with that email exists, a reset token will be shown'), 'info')
        
        return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Find user by reset token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or user.reset_token_expiry < datetime.utcnow():
        flash(_('Invalid or expired reset token'), 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password != confirm_password:
            flash(_('New passwords do not match'), 'error')
            return redirect(url_for('reset_password', token=token))
        
        if not validate_password_strength(new_password):
            flash(_('Password must be at least 8 chars and include upper, lower, digit, and special.'), 'error')
            return redirect(url_for('reset_password', token=token))
        
        # Update password and clear reset token
        user.password = generate_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash(_('Password reset successful. You can now login with your new password.'), 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)
'''

# Find the logout route and insert the reset routes before it
logout_pattern = r'@app.route\(\'/logout\'\)'

if re.search(logout_pattern, content):
    # Insert the reset routes before the logout route
    updated_content = re.sub(logout_pattern, reset_routes + '@app.route(\'/logout\')', content)
    
    # Write the updated content back to the file with UTF-8 encoding
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print('Successfully added password reset routes to app.py')
else:
    print('Could not find logout route to insert password reset routes')

