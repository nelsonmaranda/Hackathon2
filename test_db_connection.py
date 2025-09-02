#!/usr/bin/env python3
"""
Simple database connection test script
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_railway_connection():
    """Test connection to Railway PostgreSQL database"""
    print("🔍 Testing Database Connection...")
    print("=" * 50)
    
    # Get database configuration from environment
    db_type = os.getenv('DB_TYPE', 'mysql')
    
    if db_type == 'postgresql':
        db_config = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': int(os.getenv('DB_PORT', '5432'))
        }
    else:
        db_config = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'charset': 'utf8mb4',
            'autocommit': True,
            'ssl_disabled': True
        }
    
    print(f"Database Type: {db_type}")
    print(f"Host: {db_config['host']}")
    print(f"Database: {db_config['database']}")
    print(f"User: {db_config['user']}")
    print(f"Port: {db_config['port']}")
    print(f"Password: {'*' * len(db_config['password']) if db_config['password'] else 'NOT SET'}")
    print("-" * 50)
    
    try:
        print("🔄 Attempting to connect...")
        
        if db_type == 'postgresql':
            import psycopg2
            connection = psycopg2.connect(**db_config)
            
            # Test basic query
            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            print("✅ Connection successful!")
            print(f"PostgreSQL version: {version[0]}")
            
            # Test if tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            
        else:
            import pymysql
            connection = pymysql.connect(**db_config)
            
            # Test basic query
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
            
            print("✅ Connection successful!")
            print(f"MySQL version: {version[0]}")
            
            # Test if tables exist
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("📋 No tables found (database might be empty)")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        if db_type == 'mysql':
            print("1. Check if MySQL service is running")
            print("2. Verify root user has no password or set a password")
            print("3. Check if 'eduverse' database exists")
        else:
            print("1. Check if DB_HOST is the external Railway URL")
            print("2. Verify your Railway database is running")
            print("3. Check if the credentials are correct")
        return False

if __name__ == "__main__":
    test_railway_connection()
