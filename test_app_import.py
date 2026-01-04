#!/usr/bin/env python3
"""
Test script to verify app.py can be imported correctly.
"""
import sys
import traceback

def main():
    print("Testing app.py import...")
    
    try:
        # Add current directory to path
        if '.' not in sys.path:
            sys.path.insert(0, '.')
        
        # Try to import the app
        from app import app, create_tables
        print("✅ Successfully imported app from app.py")
        
        # Check app configuration
        print(f"   - Debug mode: {app.debug}")
        print(f"   - Secret key set: {app.secret_key is not None}")
        
        # Check database initialization
        print("Testing database initialization...")
        create_tables()
        print("✅ Database initialized successfully")
        
        # Check routes
        routes = list(app.url_map.iter_rules())
        print(f"✅ Found {len(routes)} routes:")
        for route in routes:
            if not route.rule.startswith('/static'):
                methods = ', '.join(sorted(route.methods))
                print(f"   - {route.rule} [{methods}]")
        
        print("\n🎉 All tests passed! app.py is working correctly.")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print("Traceback:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())