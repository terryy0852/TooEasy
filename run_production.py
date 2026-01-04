from app import app, create_tables

# Initialize database and run app without debug mode
create_tables()
app.run(debug=False, host='0.0.0.0', port=5000)
