#!/usr/bin/env python3
"""
Quick fix script to temporarily bypass database issues for testing
This is NOT for production use!
"""
import os

def create_railway_env():
    """Create a Railway-compatible .env file"""
    
    env_content = """# Railway Database Configuration
# Add these to your Railway environment variables

# Database Type (choose one)
DB_TYPE=postgresql

# PostgreSQL (Railway default)
DB_HOST=${PGHOST}
DB_NAME=${PGDATABASE}
DB_USER=${PGUSER}
DB_PASSWORD=${PGPASSWORD}
DB_PORT=${PGPORT}

# MySQL (if using external service)
# DB_HOST=your-mysql-host
# DB_NAME=your-mysql-database
# DB_USER=your-mysql-user
# DB_PASSWORD=your-mysql-password
# DB_PORT=3306

# Required Environment Variables
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
HUGGINGFACE_API_KEY=your-huggingface-api-key

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Payment (optional)
INTASEND_PUBLISHABLE_KEY=your-intasend-key
INTASEND_SECRET_KEY=your-intasend-secret
INTASEND_TEST_MODE=True

# App Configuration
SUBSCRIPTION_AMOUNT=12.00
SUBSCRIPTION_CURRENCY=USD
SUBSCRIPTION_DURATION_DAYS=30
TRIAL_DURATION_DAYS=7
MAX_FLASHCARDS_PER_GENERATION=20
MIN_FLASHCARDS_PER_GENERATION=1
"""
    
    with open('railway.env.example', 'w') as f:
        f.write(env_content)
    
    print("✅ Created railway.env.example")
    print("📝 Copy these variables to your Railway environment")

def show_railway_steps():
    """Show step-by-step Railway setup"""
    
    steps = """
🚀 RAILWAY DATABASE SETUP STEPS:

1. GO TO RAILWAY DASHBOARD:
   - Visit: https://railway.app/dashboard
   - Select your EduVerse project

2. ADD POSTGRESQL DATABASE:
   - Click "New Service"
   - Select "Database" → "PostgreSQL"
   - Wait for provisioning

3. CONNECT DATABASE TO APP:
   - In your app service, go to "Variables"
   - Add these environment variables:
     DB_TYPE=postgresql
     DB_HOST=${PGHOST}
     DB_NAME=${PGDATABASE}
     DB_USER=${PGUSER}
     DB_PASSWORD=${PGPASSWORD}
     DB_PORT=${PGPORT}

4. ADD OTHER REQUIRED VARIABLES:
   - SECRET_KEY (generate a random string)
   - MAIL_USERNAME (your Gmail)
   - MAIL_PASSWORD (Gmail app password)
   - HUGGINGFACE_API_KEY (optional)

5. REDEPLOY:
   - Railway will auto-deploy
   - Test signup page again

🔗 TEST URL: https://eduverseai.up.railway.app/signup
"""
    
    print(steps)

def show_quick_test_fix():
    """Show how to quickly test without database"""
    
    fix = """
⚡ QUICK TEST FIX (Temporary):

If you want to test the app immediately without setting up a database:

1. Edit app.py, find the EduVerse class __init__ method
2. Change this line:
   self.db_available = False
   
   To this:
   self.db_available = True  # TEMPORARY FOR TESTING

3. This will bypass database checks and allow signup
4. WARNING: Data won't be saved permanently
5. REMOVE this change after setting up proper database

⚠️  This is ONLY for testing, not for production use!
"""
    
    print(fix)

if __name__ == "__main__":
    print("🔧 EduVerse Railway Database Fix")
    print("=" * 40)
    
    print("\n📋 Creating Railway environment template...")
    create_railway_env()
    
    print("\n📖 Railway Setup Instructions:")
    show_railway_steps()
    
    print("\n⚡ Quick Test Option:")
    show_quick_test_fix()
    
    print("\n🎯 Next Steps:")
    print("1. Follow the Railway setup steps above")
    print("2. Or use the quick test fix temporarily")
    print("3. Test your signup page again")
    print("4. The 'database not available' error should be resolved")
