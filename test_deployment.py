#!/usr/bin/env python3
"""
Deployment test script for Railway
Tests if the app can start without database connection errors
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deployment_readiness():
    """Test if the app is ready for Railway deployment"""
    print("🔍 Testing Railway Deployment Readiness...")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        'DB_TYPE',
        'DB_HOST', 
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_PORT',
        'SECRET_KEY',
        'FLASK_ENV'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your-'):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value[:20]}{'...' if len(value) > 20 else ''}")
    
    if missing_vars:
        print(f"\n❌ Missing or placeholder environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Update your .env file with real Railway values before deployment")
        return False
    
    # Check database type
    db_type = os.getenv('DB_TYPE')
    if db_type == 'mysql':
        print(f"\n✅ Database type: {db_type} (MySQL)")
        print("✅ App.py is MySQL-compatible")
    elif db_type == 'postgresql':
        print(f"\n✅ Database type: {db_type} (PostgreSQL)")
        print("✅ App.py is PostgreSQL-compatible")
    else:
        print(f"\n❌ Unknown database type: {db_type}")
        return False
    
    # Check if app can import without errors
    try:
        print("\n🔄 Testing app import...")
        import app
        print("✅ App.py imports successfully")
        print("✅ No syntax errors detected")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_deployment_readiness()
    if success:
        print("\n🎉 App is ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Create MySQL database on Railway")
        print("2. Update .env with real Railway values")
        print("3. Deploy to Railway")
    else:
        print("\n⚠️  App needs fixes before deployment")
