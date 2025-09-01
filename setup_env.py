#!/usr/bin/env python3
"""
Environment setup script for EduVerse
Run this script to create a .env file with your configuration
"""
import os
import secrets

def create_env_file():
    """Create a .env file with default configuration"""
    
    if os.path.exists('.env'):
        print("Warning: .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Generate a secure secret key
    secret_key = secrets.token_hex(32)
    
    env_content = f"""# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_NAME=eduverse
DB_USER=root
DB_PASSWORD=your-database-password

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Hugging Face API
HUGGINGFACE_API_KEY=your-huggingface-api-key

# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# IntaSend Payment Configuration
INTASEND_PUBLISHABLE_KEY=your-intasend-publishable-key
INTASEND_SECRET_KEY=your-intasend-secret-key
INTASEND_TEST_MODE=True

# Application Configuration
SUBSCRIPTION_AMOUNT=12.00
SUBSCRIPTION_CURRENCY=USD
SUBSCRIPTION_DURATION_DAYS=30
TRIAL_DURATION_DAYS=7
MAX_FLASHCARDS_PER_GENERATION=20
MIN_FLASHCARDS_PER_GENERATION=1
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print("📝 Please edit the .env file with your actual configuration values.")
    print("🔑 A secure SECRET_KEY has been generated for you.")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask', 'authlib', 'flask_mail', 'requests', 
        'pymysql', 'dotenv', 'intasend'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages are installed!")
        return True

if __name__ == "__main__":
    print("🚀 EduVerse Environment Setup")
    print("=" * 40)
    
    print("\n📦 Checking dependencies...")
    deps_ok = check_dependencies()
    
    if deps_ok:
        print("\n🔧 Setting up environment...")
        create_env_file()
        
        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Edit the .env file with your configuration")
        print("2. Set up your database")
        print("3. Configure your OAuth providers")
        print("4. Run: python app.py")
    else:
        print("\n❌ Please install missing dependencies first.")
