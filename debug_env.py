#!/usr/bin/env python3
"""
Debug script to check environment variables
"""
import os
from dotenv import load_dotenv

print("🔍 Debugging Environment Variables...")
print("=" * 50)

# Check before loading .env
print("Before load_dotenv():")
print(f"DB_TYPE: {os.getenv('DB_TYPE', 'NOT SET')}")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT SET')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")

print("\n" + "=" * 50)

# Load .env file
print("Loading .env file...")
load_dotenv()

print("\nAfter load_dotenv():")
print(f"DB_TYPE: {os.getenv('DB_TYPE', 'NOT SET')}")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT SET')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")

print("\n" + "=" * 50)

# Check if .env file exists and its content
env_path = os.path.join(os.getcwd(), '.env')
print(f"Checking .env file at: {env_path}")
if os.path.exists(env_path):
    print("✅ .env file exists")
    with open(env_path, 'r') as f:
        content = f.read()
        print(f"Content length: {len(content)} characters")
        print("First few lines:")
        for i, line in enumerate(content.split('\n')[:10]):
            print(f"  {i+1}: {line}")
else:
    print("❌ .env file does not exist")

print("\n" + "=" * 50)

# Check current working directory
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory:")
for file in os.listdir('.'):
    if file.startswith('.env') or file.endswith('.env'):
        print(f"  - {file}")
