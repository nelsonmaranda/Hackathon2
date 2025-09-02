#!/usr/bin/env python3
"""
Simple MySQL connection test
"""
import os
from dotenv import load_dotenv
import pymysql

# Load environment variables
load_dotenv()

def test_mysql_connection():
    """Test MySQL connection only"""
    print("🔍 Testing MySQL Connection...")
    print("=" * 50)
    
    # Get MySQL configuration from environment
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'test'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': int(os.getenv('DB_PORT', '3306')),
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    print("MySQL Configuration:")
    print(f"Host: {db_config['host']}")
    print(f"Database: {db_config['database']}")
    print(f"User: {db_config['user']}")
    print(f"Port: {db_config['port']}")
    print(f"Password: {'*' * len(db_config['password']) if db_config['password'] else 'EMPTY'}")
    print("-" * 50)
    
    # Check if we have placeholder values
    if db_config['host'].startswith('your-'):
        print("❌ Error: Using placeholder values!")
        print("Please update your .env file with real MySQL connection details:")
        print("1. Create a MySQL database on Railway")
        print("2. Copy the connection details to your .env file")
        print("3. Replace 'your-railway-mysql-host' with the actual host")
        return False
    
    try:
        print("🔄 Attempting MySQL connection...")
        connection = pymysql.connect(**db_config)
        
        # Test basic query
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        
        print("✅ MySQL connection successful!")
        print(f"MySQL version: {version[0]}")
        
        # Test if database exists
        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()
        
        print(f"📋 Available databases:")
        for db in databases:
            print(f"  - {db[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure MySQL is running")
        print("2. Check your credentials")
        print("3. Verify the host and port")
        print("4. Make sure the database exists")
        return False

if __name__ == "__main__":
    test_mysql_connection()
