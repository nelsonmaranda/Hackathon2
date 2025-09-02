from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash  # pyright: ignore[reportMissingImports]
from authlib.integrations.flask_client import OAuth  # pyright: ignore[reportMissingImports]
from flask_mail import Mail, Message  # pyright: ignore[reportMissingImports]
from functools import wraps
import requests  # pyright: ignore[reportMissingModuleSource]
import os
import json
import re
import uuid
import random
from datetime import datetime, timedelta
import psycopg2  # pyright: ignore[reportMissingModuleSource]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
import hashlib
import secrets
import intasend  # pyright: ignore[reportMissingImports]

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', '')

mail = Mail(app)

# Hugging Face API configuration
HF_API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}

# Database configuration
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')
if DB_TYPE == 'postgresql':
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': os.getenv('DB_PORT')
    }
else:
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': os.getenv('DB_PORT', '3306'),
        'charset': 'utf8mb4',
        'autocommit': True,
        'ssl_disabled': True
    }

def get_db_connection():
    """Get database connection based on DB_TYPE"""
    if DB_TYPE == 'postgresql':
        return psycopg2.connect(**DB_CONFIG)
    else:
        import pymysql
        return pymysql.connect(**DB_CONFIG)

# Store verification codes (in production, use database)
verification_codes = {}

# Rate limiting storage (in production, use Redis or database)
rate_limit_store = {}

# IntaSend Payment Configuration
INTASEND_PUBLISHABLE_KEY = os.getenv('INTASEND_PUBLISHABLE_KEY')
INTASEND_SECRET_KEY = os.getenv('INTASEND_SECRET_KEY')
INTASEND_TEST_MODE = os.getenv('INTASEND_TEST_MODE', 'True').lower() == 'true'

# Initialize IntaSend service
intasend_service = None
if INTASEND_PUBLISHABLE_KEY and INTASEND_SECRET_KEY:
    try:
        # Try different import patterns for older versions
        if hasattr(intasend, 'IntaSend'):
            intasend_service = intasend.IntaSend(
                token=INTASEND_SECRET_KEY,
                publishable_key=INTASEND_PUBLISHABLE_KEY,
                test=INTASEND_TEST_MODE
            )
        elif hasattr(intasend, 'APIService'):
            intasend_service = intasend.APIService(
                token=INTASEND_SECRET_KEY,
                publishable_key=INTASEND_PUBLISHABLE_KEY,
                test=INTASEND_TEST_MODE
            )
        else:
            print("Warning: IntaSend service not properly configured")
    except Exception as e:
        print(f"Warning: IntaSend initialization failed: {e}")
        intasend_service = None

# OAuth configuration
oauth = OAuth(app)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
    oauth.register(
        name='github',
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'read:user user:email'}
    )

# Add OAuth credentials to app config for template access
app.config['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET
app.config['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
app.config['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET

class EduVerse:
    def __init__(self):
        self.db_available = False
        self.setup_database()
    
    def setup_database(self):
        """Initialize database tables"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Create users table
            if DB_TYPE == 'postgresql':
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        email_verified BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        email_verified BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            # Create flashcards table
            if DB_TYPE == 'postgresql':
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS flashcards (
                        id SERIAL PRIMARY KEY,
                        user_id INT,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        topic VARCHAR(255),
                        difficulty VARCHAR(10) DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
                        question_type VARCHAR(50) DEFAULT 'short_answer',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_reviewed TIMESTAMP NULL,
                        review_count INT DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS flashcards (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        topic VARCHAR(255),
                        difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
                        question_type VARCHAR(50) DEFAULT 'short_answer',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_reviewed TIMESTAMP NULL,
                        review_count INT DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
            
            # Create study_sessions table
            if DB_TYPE == 'postgresql':
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS study_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INT,
                        session_date DATE,
                        cards_studied INT DEFAULT 0,
                        correct_answers INT DEFAULT 0,
                        total_time_minutes INT DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS study_sessions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        session_date DATE,
                        cards_studied INT DEFAULT 0,
                        correct_answers INT DEFAULT 0,
                        total_time_minutes INT DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
            
            # Create subscriptions table
            if DB_TYPE == 'postgresql':
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id SERIAL PRIMARY KEY,
                        user_id INT UNIQUE,
                        subscription_type VARCHAR(10) DEFAULT 'trial' CHECK (subscription_type IN ('trial', 'premium')),
                        status VARCHAR(10) DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
                        trial_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        trial_end_date TIMESTAMP,
                        subscription_start_date TIMESTAMP NULL,
                        subscription_end_date TIMESTAMP NULL,
                        intasend_payment_id VARCHAR(255) NULL,
                        amount_paid DECIMAL(10,2) DEFAULT 0.00,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT UNIQUE,
                        subscription_type ENUM('trial', 'premium') DEFAULT 'trial',
                        status ENUM('active', 'cancelled', 'expired') DEFAULT 'active',
                        trial_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        trial_end_date TIMESTAMP,
                        subscription_start_date TIMESTAMP NULL,
                        subscription_end_date TIMESTAMP NULL,
                        intasend_payment_id VARCHAR(255) NULL,
                        amount_paid DECIMAL(10,2) DEFAULT 0.00,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
            
            connection.commit()
            
            # Check if we need to add new columns to existing tables
            self._upgrade_database_schema(connection)
            
            self.db_available = True
            print("Database setup completed successfully!")
            
        except Exception as e:
            print(f"Database setup failed: {e}")
            self.db_available = False
        finally:
            if 'connection' in locals():
                connection.close()
    
    def test_connection(self):
        """Test if database connection is working"""
        try:
            if self.db_available:
                connection = get_db_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                connection.close()
                return True
            return False
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False
    
    def _upgrade_database_schema(self, connection):
        """Upgrade database schema to add new columns if they don't exist"""
        try:
            cursor = connection.cursor()
            
            if DB_TYPE == 'postgresql':
                # PostgreSQL syntax for checking columns
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'flashcards' AND column_name = 'question_type'
                """)
                if not cursor.fetchone():
                    print("Adding question_type column to flashcards table...")
                    cursor.execute("ALTER TABLE flashcards ADD COLUMN question_type VARCHAR(50) DEFAULT 'short_answer'")
                
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'flashcards' AND column_name = 'difficulty'
                """)
                if not cursor.fetchone():
                    print("Adding difficulty column to flashcards table...")
                    cursor.execute("ALTER TABLE flashcards ADD COLUMN difficulty VARCHAR(10) DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard'))")
            else:
                # MySQL syntax for checking columns
                cursor.execute("SHOW COLUMNS FROM flashcards LIKE 'question_type'")
                if not cursor.fetchone():
                    print("Adding question_type column to flashcards table...")
                    cursor.execute("ALTER TABLE flashcards ADD COLUMN question_type VARCHAR(50) DEFAULT 'short_answer'")
                
                cursor.execute("SHOW COLUMNS FROM flashcards LIKE 'difficulty'")
                if not cursor.fetchone():
                    print("Adding difficulty column to flashcards table...")
                    cursor.execute("ALTER TABLE flashcards ADD COLUMN difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium'")
            
            connection.commit()
            print("Database schema upgrade completed!")
            
        except Exception as e:
            print(f"Error upgrading database schema: {e}")
            connection.rollback()
    
    def test_database_connection(self):
        """Test database connection and return status"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            connection.close()
            return True, "Database connection successful"
        except Exception as e:
            return False, f"Database connection failed: {e}"
    
    def start_study_session(self, user_id, topic):
        """Start a new study session"""
        if not self.db_available:
            return None
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            if DB_TYPE == 'postgresql':
                cursor.execute("""
                    INSERT INTO study_sessions (user_id, session_date, cards_studied, correct_answers, total_time_minutes)
                    VALUES (%s, CURRENT_DATE, 0, 0, 0)
                """, (user_id,))
            else:
                cursor.execute("""
                    INSERT INTO study_sessions (user_id, session_date, cards_studied, correct_answers, total_time_minutes)
                    VALUES (%s, CURDATE(), 0, 0, 0)
                """, (user_id,))
            
            connection.commit()
            if DB_TYPE == 'postgresql':
                cursor.execute("SELECT LASTVAL()")
                session_id = cursor.fetchone()[0]
            else:
                session_id = cursor.lastrowid
            connection.close()
            return session_id
            
        except Exception as e:
            print(f"Error starting study session: {e}")
            return None
    
    def update_study_session(self, session_id, cards_studied, correct_answers, time_minutes):
        """Update study session with results"""
        if not self.db_available:
            return False
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE study_sessions 
                SET cards_studied = %s, correct_answers = %s, total_time_minutes = %s
                WHERE id = %s
            """, (cards_studied, correct_answers, time_minutes, session_id))
            
            connection.commit()
            connection.close()
            return True
            
        except Exception as e:
            print(f"Error updating study session: {e}")
            return False
    
    def get_user_stats(self, user_id):
        """Get user's study statistics"""
        if not self.db_available:
            return {'total_sessions': 0, 'total_cards': 0, 'total_correct': 0, 'success_rate': 0}
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(cards_studied) as total_cards,
                    SUM(correct_answers) as total_correct
                FROM study_sessions 
                WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            connection.close()
            
            if result and result[0]:
                total_sessions = result[0]
                total_cards = result[1] or 0
                total_correct = result[2] or 0
                success_rate = round((total_correct / total_cards * 100) if total_cards > 0 else 0, 1)
                
                return {
                    'total_sessions': total_sessions,
                    'total_cards': total_cards,
                    'total_correct': total_correct,
                    'success_rate': success_rate
                }
            else:
                return {'total_sessions': 0, 'total_cards': 0, 'total_correct': 0, 'success_rate': 0}
                
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {'total_sessions': 0, 'total_cards': 0, 'total_correct': 0, 'success_rate': 0}
    
    def get_flashcard_by_id(self, flashcard_id, user_id):
        """Get a specific flashcard by ID for editing"""
        if not self.db_available:
            return None
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT id, question, answer, topic, difficulty, question_type
                FROM flashcards 
                WHERE id = %s AND user_id = %s
            """, (flashcard_id, user_id))
            
            result = cursor.fetchone()
            connection.close()
            
            if result:
                return {
                    'id': result[0],
                    'question': result[1],
                    'answer': result[2],
                    'topic': result[3],
                    'difficulty': result[4],
                    'question_type': result[5]
                }
            return None
            
        except Exception as e:
            print(f"Error getting flashcard: {e}")
            return None
    
    def update_flashcard(self, flashcard_id, user_id, question, answer, topic, difficulty, question_type):
        """Update an existing flashcard"""
        if not self.db_available:
            return False
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE flashcards 
                SET question = %s, answer = %s, topic = %s, difficulty = %s, question_type = %s
                WHERE id = %s AND user_id = %s
            """, (question, answer, topic, difficulty, question_type, flashcard_id, user_id))
            
            connection.commit()
            connection.close()
            return True
            
        except Exception as e:
            print(f"Error updating flashcard: {e}")
            return False
    
    def delete_flashcard(self, flashcard_id, user_id):
        """Delete a flashcard"""
        if not self.db_available:
            return False
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                DELETE FROM flashcards 
                WHERE id = %s AND user_id = %s
            """, (flashcard_id, user_id))
            
            connection.commit()
            connection.close()
            return True
            
        except Exception as e:
            print(f"Error deleting flashcard: {e}")
            return False
    
    def get_user_subscription(self, user_id):
        """Get user's subscription details"""
        if not self.db_available:
            return None
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT subscription_type, status, trial_start_date, trial_end_date,
                       subscription_start_date, subscription_end_date, amount_paid
                FROM subscriptions 
                WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            connection.close()
            
            if result:
                return {
                    'subscription_type': result[0],
                    'status': result[1],
                    'trial_start_date': result[2],
                    'trial_end_date': result[3],
                    'subscription_start_date': result[4],
                    'subscription_end_date': result[5],
                    'amount_paid': result[6]
                }
            return None
            
        except Exception as e:
            print(f"Error getting subscription: {e}")
            return None
    
    def is_subscription_active(self, user_id):
        """Check if user has active subscription or trial"""
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return False
        
        now = datetime.now()
        
        # Check trial period
        if subscription['subscription_type'] == 'trial':
            if subscription['trial_end_date'] and now <= subscription['trial_end_date']:
                return True
            else:
                # Trial expired, update status
                self.expire_subscription(user_id)
                return False
        
        # Check premium subscription
        if subscription['subscription_type'] == 'premium':
            if subscription['subscription_end_date'] and now <= subscription['subscription_end_date']:
                return True
            else:
                # Premium expired, update status
                self.expire_subscription(user_id)
                return False
        
        return False
    
    def expire_subscription(self, user_id):
        """Mark subscription as expired"""
        if not self.db_available:
            return False
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE subscriptions 
                SET status = 'expired'
                WHERE user_id = %s
            """, (user_id,))
            
            connection.commit()
            connection.close()
            return True
            
        except Exception as e:
            print(f"Error expiring subscription: {e}")
            return False
    
    def upgrade_to_premium(self, user_id, payment_id, amount_paid):
        """Upgrade user to premium subscription"""
        if not self.db_available:
            return False
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            subscription_start = datetime.now()
            subscription_end = subscription_start + timedelta(days=30)  # 30-day subscription
            
            cursor.execute("""
                UPDATE subscriptions 
                SET subscription_type = 'premium',
                    status = 'active',
                    subscription_start_date = %s,
                    subscription_end_date = %s,
                    intasend_payment_id = %s,
                    amount_paid = %s,
                    updated_at = %s
                WHERE user_id = %s
            """, (subscription_start, subscription_end, payment_id, amount_paid, datetime.now(), user_id))
            
            connection.commit()
            connection.close()
            return True
            
        except Exception as e:
            print(f"Error upgrading subscription: {e}")
            return False
    
    def get_days_remaining(self, user_id):
        """Get days remaining in current subscription"""
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return 0
        
        now = datetime.now()
        
        if subscription['subscription_type'] == 'trial' and subscription['trial_end_date']:
            delta = subscription['trial_end_date'] - now
            return max(0, delta.days)
        elif subscription['subscription_type'] == 'premium' and subscription['subscription_end_date']:
            delta = subscription['subscription_end_date'] - now
            return max(0, delta.days)
        
        return 0
    
    def create_user(self, username, email, password):
        """Create a new user"""
        if not self.db_available:
            return False, "Database not available"
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            if DB_TYPE == 'postgresql':
                cursor.execute("SELECT LASTVAL()")
                user_id = cursor.fetchone()[0]
            else:
                user_id = cursor.lastrowid
            
            # Create trial subscription for new user
            trial_end_date = datetime.now() + timedelta(days=7)
            cursor.execute("""
                INSERT INTO subscriptions (user_id, subscription_type, status, trial_end_date)
                VALUES (%s, 'trial', 'active', %s)
            """, (user_id, trial_end_date))
            
            connection.commit()
            return True, "User created successfully"
            
        except Exception as e:
            if "Duplicate entry" in str(e) or "duplicate key" in str(e).lower():
                return False, "Username or email already exists"
            return False, f"Error creating user: {e}"
        finally:
            if 'connection' in locals():
                connection.close()
    
    def verify_user(self, username, password):
        """Verify user login"""
        if not self.db_available:
            return None
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute(
                "SELECT id, username, email, email_verified FROM users WHERE username = %s AND password_hash = %s",
                (username, password_hash)
            )
            
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'email_verified': user[3]
                }
            return None
            
        except Exception as e:
            print(f"Error verifying user: {e}")
            return None
        finally:
            if 'connection' in locals():
                connection.close()

    def get_user_by_email(self, email):
        """Fetch user by email"""
        if not self.db_available:
            return None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, username, email, email_verified FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'email_verified': user[3]
                }
            return None
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None
        finally:
            if 'connection' in locals():
                connection.close()

    def create_oauth_user(self, username, email):
        """Create a user for OAuth logins (no password)"""
        if not self.db_available:
            return None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            # Use a placeholder password hash; user authenticates via provider
            placeholder_hash = hashlib.sha256((email + 'oauth').encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, email_verified) VALUES (%s, %s, %s, TRUE)",
                (username, email, placeholder_hash)
            )
            connection.commit()
            # Return created user
            return self.get_user_by_email(email)
        except Exception:
            # If user already exists, just return it
            return self.get_user_by_email(email)
        except Exception as e:
            print(f"Error creating OAuth user: {e}")
            return None
        finally:
            if 'connection' in locals():
                connection.close()
    
    def generate_flashcards(self, notes, num_cards=5):
        """Generate flashcards using Hugging Face API with improved prompting"""
        try:
            # Enhanced prompt for better question generation
            prompt = f"""Based on the following study notes, generate {num_cards} diverse and challenging quiz questions. 
            
            Requirements:
            - Create different types of questions: multiple choice, fill-in-the-blank, true/false, and short answer
            - Questions should test different levels of understanding: recall, comprehension, application, and analysis
            - Make questions engaging and thought-provoking
            - Ensure answers are clear and educational
            
            Format the response as a JSON array: [{{"question": "question text", "answer": "answer text", "type": "question_type", "difficulty": "easy/medium/hard"}}]
            
            Study Notes:
            {notes}
            
            Generate exactly {num_cards} questions:"""
            
            response = requests.post(
                HF_API_URL,
                headers=HF_HEADERS,
                json={"inputs": prompt}
            )
            
            if response.status_code == 200:
                try:
                    response_text = response.json()[0]['generated_text']
                    
                    # Look for JSON pattern in the response
                    json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                    if json_match:
                        cards_data = json.loads(json_match.group())
                        # Validate and clean the generated cards
                        return self._validate_and_clean_cards(cards_data, num_cards)
                    else:
                        return self._generate_enhanced_fallback_cards(notes, num_cards)
                        
                except (json.JSONDecodeError, KeyError, IndexError):
                    return self._generate_enhanced_fallback_cards(notes, num_cards)
            else:
                return self._generate_enhanced_fallback_cards(notes, num_cards)
                
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            return self._generate_enhanced_fallback_cards(notes, num_cards)
    
    def _validate_and_clean_cards(self, cards_data, num_cards):
        """Validate and clean generated flashcards"""
        valid_cards = []
        
        for card in cards_data:
            if isinstance(card, dict) and 'question' in card and 'answer' in card:
                # Ensure question and answer are not empty
                if card['question'].strip() and card['answer'].strip():
                    # Clean and format the card
                    cleaned_card = {
                        'question': card['question'].strip(),
                        'answer': card['answer'].strip(),
                        'type': card.get('type', 'short_answer'),
                        'difficulty': card.get('difficulty', 'medium')
                    }
                    valid_cards.append(cleaned_card)
        
        # If we don't have enough valid cards, generate fallback ones
        if len(valid_cards) < num_cards:
            remaining = num_cards - len(valid_cards)
            fallback_cards = self._generate_enhanced_fallback_cards("", remaining)
            valid_cards.extend(fallback_cards)
        
        return valid_cards[:num_cards]
    
    def _generate_enhanced_fallback_cards(self, notes, num_cards):
        """Generate enhanced flashcards when AI fails"""
        cards = []
        
        if notes.strip():
            # Extract key concepts and terms
            key_terms = self._extract_key_terms(notes)
            sentences = self._extract_meaningful_sentences(notes)
            
            # Create different types of questions
            question_types = [
                self._create_fill_blank_question,
                self._create_definition_question,
                self._create_concept_question,
                self._create_application_question,
                self._create_comparison_question
            ]
            
            for i in range(num_cards):
                if i < len(question_types):
                    question_func = question_types[i]
                    card = question_func(notes, key_terms, sentences, i)
                else:
                    # Cycle through question types
                    question_func = question_types[i % len(question_types)]
                    card = question_func(notes, key_terms, sentences, i)
                
                if card:
                    cards.append(card)
        else:
            # Generate generic educational questions
            cards = self._generate_generic_questions(num_cards)
        
        return cards[:num_cards]
    
    def _extract_key_terms(self, notes):
        """Extract important terms and concepts from notes"""
        # Remove common words and extract capitalized terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can'}
        
        words = re.findall(r'\b[A-Z][a-z]+\b', notes)
        words.extend(re.findall(r'\b[a-z]{4,}\b', notes.lower()))
        
        # Filter out common words and duplicates
        key_terms = [word for word in words if word.lower() not in common_words]
        return list(set(key_terms))[:10]  # Limit to top 10 terms
    
    def _extract_meaningful_sentences(self, notes):
        """Extract meaningful sentences from notes"""
        sentences = re.split(r'[.!?]+', notes)
        meaningful_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15 and len(sentence) < 200:  # Reasonable length
                # Check if sentence contains key information
                if any(word in sentence.lower() for word in ['is', 'are', 'means', 'refers', 'consists', 'includes', 'involves', 'process', 'system', 'method', 'theory', 'principle']):
                    meaningful_sentences.append(sentence)
        
        return meaningful_sentences[:5]  # Limit to top 5 sentences
    
    def _create_fill_blank_question(self, notes, key_terms, sentences, index):
        """Create a fill-in-the-blank question"""
        if key_terms and sentences:
            term = random.choice(key_terms)
            sentence = random.choice(sentences)
            
            # Create a fill-in-the-blank question
            question = sentence.replace(term, "_____")
            return {
                "question": f"Fill in the blank: {question}",
                "answer": term,
                "type": "fill_blank",
                "difficulty": "easy"
            }
        return None
    
    def _create_definition_question(self, notes, key_terms, sentences, index):
        """Create a definition question"""
        if key_terms:
            term = random.choice(key_terms)
            return {
                "question": f"What is the definition of '{term}'?",
                "answer": f"'{term}' refers to a concept or term mentioned in the study notes. Review the notes for its specific definition.",
                "type": "definition",
                "difficulty": "medium"
            }
        return None
    
    def _create_concept_question(self, notes, key_terms, sentences, index):
        """Create a concept understanding question"""
        if sentences:
            sentence = random.choice(sentences)
            return {
                "question": f"Explain the concept described in this statement: '{sentence}'",
                "answer": "This statement describes a key concept from your study notes. Review the context and related information to provide a comprehensive explanation.",
                "type": "concept",
                "difficulty": "hard"
            }
        return None
    
    def _create_application_question(self, notes, key_terms, sentences, index):
        """Create an application question"""
        if key_terms:
            term = random.choice(key_terms)
            return {
                "question": f"How would you apply the concept of '{term}' in a real-world scenario?",
                "answer": "Consider practical applications of this concept. Think about how it relates to everyday situations or professional contexts.",
                "type": "application",
                "difficulty": "hard"
            }
        return None
    
    def _create_comparison_question(self, notes, key_terms, sentences, index):
        """Create a comparison question"""
        if len(key_terms) >= 2:
            term1, term2 = random.sample(key_terms, 2)
            return {
                "question": f"What are the key differences between '{term1}' and '{term2}'?",
                "answer": f"Compare and contrast these two concepts. Consider their definitions, characteristics, and how they relate to each other.",
                "type": "comparison",
                "difficulty": "medium"
            }
        return None
    
    def _generate_generic_questions(self, num_cards):
        """Generate generic educational questions when no notes are provided"""
        generic_questions = [
            {
                "question": "What is the main purpose of taking study notes?",
                "answer": "Study notes help organize information, improve retention, and serve as a reference for review and learning.",
                "type": "concept",
                "difficulty": "easy"
            },
            {
                "question": "How can you make your study notes more effective?",
                "answer": "Use clear organization, include key concepts, add examples, review regularly, and connect related ideas.",
                "type": "application",
                "difficulty": "medium"
            },
            {
                "question": "What is the difference between active and passive learning?",
                "answer": "Active learning involves engagement, practice, and application, while passive learning is simply receiving information without interaction.",
                "type": "comparison",
                "difficulty": "medium"
            },
            {
                "question": "Why is it important to review study materials regularly?",
                "answer": "Regular review strengthens memory, reinforces learning, identifies knowledge gaps, and improves long-term retention.",
                "type": "concept",
                "difficulty": "easy"
            },
            {
                "question": "How can flashcards improve your study efficiency?",
                "answer": "Flashcards promote active recall, spaced repetition, quick review, and help identify areas that need more attention.",
                "type": "application",
                "difficulty": "medium"
            }
        ]
        
        return generic_questions[:num_cards]
    
    def save_flashcards(self, user_id, cards, topic):
        """Save flashcards to database"""
        if not self.db_available:
            print("Database not available")
            return False
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # First, let's check if the table has the new columns
            if DB_TYPE == 'postgresql':
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'flashcards'
                """)
            else:
                cursor.execute("DESCRIBE flashcards")
            columns = [column[0] for column in cursor.fetchall()]
            
            for card in cards:
                if 'question_type' in columns and 'difficulty' in columns:
                    # Use the new schema with question_type and difficulty
                    cursor.execute("""
                        INSERT INTO flashcards (user_id, question, answer, topic, question_type, difficulty)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, card['question'], card['answer'], topic, 
                          card.get('type', 'short_answer'), card.get('difficulty', 'medium')))
                else:
                    # Fallback to basic schema
                    cursor.execute("""
                        INSERT INTO flashcards (user_id, question, answer, topic)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, card['question'], card['answer'], topic))
            
            connection.commit()
            print(f"Successfully saved {len(cards)} flashcards")
            return True
            
        except Exception as e:
            print(f"Error saving flashcards: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if 'connection' in locals():
                connection.close()
    
    def get_user_flashcards(self, user_id, topic=None):
        """Get flashcards for a user"""
        if not self.db_available:
            return []
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            if topic:
                cursor.execute("""
                    SELECT id, question, answer, topic, difficulty, question_type, created_at
                    FROM flashcards WHERE user_id = %s AND topic = %s
                    ORDER BY created_at DESC
                """, (user_id, topic))
            else:
                cursor.execute("""
                    SELECT id, question, answer, topic, difficulty, question_type, created_at
                    FROM flashcards WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
            
            flashcards = []
            for row in cursor.fetchall():
                flashcards.append({
                    'id': row[0],
                    'question': row[1],
                    'answer': row[2],
                    'topic': row[3],
                    'difficulty': row[4],
                    'type': row[5],
                    'created_at': row[6]
                })
            
            return flashcards
            
        except Exception as e:
            print(f"Error getting flashcards: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

# Initialize EduVerse
try:
    eduverse = EduVerse()
    print("EduVerse initialized successfully")
except Exception as e:
    print(f"Warning: EduVerse initialization failed: {e}")
    # Create a dummy instance to prevent crashes
    class DummyEduVerse:
        def __init__(self):
            self.db_available = False
        def create_user(self, *args, **kwargs):
            return False, "Database not available"
        def verify_user(self, *args, **kwargs):
            return None
        def get_user_by_email(self, *args, **kwargs):
            return None
        def create_oauth_user(self, *args, **kwargs):
            return None
        def get_flashcards(self, *args, **kwargs):
            return []
        def create_flashcard(self, *args, **kwargs):
            return False, "Database not available"
        def update_flashcard(self, *args, **kwargs):
            return False, "Database not available"
        def delete_flashcard(self, *args, **kwargs):
            return False, "Database not available"
        def record_study_session(self, *args, **kwargs):
            return False, "Database not available"
        def get_study_stats(self, *args, **kwargs):
            return []
        def upgrade_to_premium(self, *args, **kwargs):
            return False, "Database not available"
        def subscribe(self, *args, **kwargs):
            return False, "Database not available"
        def get_subscription_status(self, *args, **kwargs):
            return {'status': 'free', 'expiry': None}
    
    eduverse = DummyEduVerse()
    print("Using dummy EduVerse instance due to initialization failure")

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Simple health check endpoint for Railway"""
    return {'status': 'healthy', 'message': 'EduVerse is running'}, 200

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return render_template('signup.html')
        
        success, message = eduverse.create_user(username, email, password)
        
        if success:
            # Send verification email
            try:
                verification_code = str(random.randint(100000, 999999))
                verification_codes[email] = verification_code
                
                msg = Message('Verify Your Email - EduVerse',
                            recipients=[email])
                msg.body = f'Your verification code is: {verification_code}'
                mail.send(msg)
                
                flash('Account created! Please check your email for verification code.')
                return redirect(url_for('verify_email', email=email))
            except Exception as e:
                flash('Account created but verification email failed. Please contact support.')
                return redirect(url_for('login'))
        else:
            flash(message)
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = eduverse.verify_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['email_verified'] = user['email_verified']
            
            flash(f'Welcome back, {user["username"]}!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    
    return render_template('login.html')

# Google OAuth
@app.route('/auth/google')
def auth_google():
    if getattr(oauth, 'google', None) is None:
        flash('Google login is not configured. Please set GOOGLE_CLIENT_ID/SECRET.')
        return redirect(url_for('login'))
    redirect_uri = url_for('auth_google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def auth_google_callback():
    try:
        token = oauth.google.authorize_access_token()
        
        # Get user info from Google userinfo endpoint instead of parse_id_token
        resp = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        userinfo = resp.json()
        
        email = userinfo.get('email')
        name = userinfo.get('name') or email.split('@')[0]
        if not email:
            flash('Google did not return an email address.')
            return redirect(url_for('login'))
        user = eduverse.get_user_by_email(email)
        if not user:
            user = eduverse.create_oauth_user(name, email)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['email_verified'] = True
            flash(f'Logged in with Google as {user["username"]}.')
            return redirect(url_for('dashboard'))
        flash('Failed to create or fetch user from Google account.')
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash('Google login failed. Please try again.')
        return redirect(url_for('login'))

# GitHub OAuth
@app.route('/auth/github')
def auth_github():
    if getattr(oauth, 'github', None) is None:
        flash('GitHub login is not configured. Please set GITHUB_CLIENT_ID/SECRET.')
        return redirect(url_for('login'))
    redirect_uri = url_for('auth_github_callback', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@app.route('/auth/github/callback')
def auth_github_callback():
    try:
        token = oauth.github.authorize_access_token()
        resp = oauth.github.get('user', token=token)
        profile = resp.json()
        email = None
        # Try primary email
        emails_resp = oauth.github.get('user/emails', token=token)
        for item in emails_resp.json():
            if item.get('primary') and item.get('verified'):
                email = item.get('email')
                break
        if not email:
            # fallback to login-based email
            email = f"{profile.get('login')}@users.noreply.github.com"
        name = profile.get('name') or profile.get('login')
        user = eduverse.get_user_by_email(email)
        if not user:
            user = eduverse.create_oauth_user(name, email)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['email_verified'] = True
            flash(f'Logged in with GitHub as {user["username"]}.')
            return redirect(url_for('dashboard'))
        flash('Failed to create or fetch user from GitHub account.')
        return redirect(url_for('login'))
    except Exception as e:
        print(f"GitHub OAuth error: {e}")
        flash('GitHub login failed. Please try again.')
        return redirect(url_for('login'))

@app.route('/verify_email/<email>', methods=['GET', 'POST'])
def verify_email(email):
    if request.method == 'POST':
        code = request.form['verification_code']
        
        if email in verification_codes and verification_codes[email] == code:
            # Mark email as verified in database
            try:
                connection = get_db_connection()
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE users SET email_verified = TRUE WHERE email = %s",
                    (email,)
                )
                connection.commit()
                
                del verification_codes[email]
                flash('Email verified successfully! You can now login.')
                return redirect(url_for('login'))
                
            except Exception as e:
                flash('Verification failed. Please try again.')
            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            flash('Invalid verification code')
    
    return render_template('verify_email.html', email=email)

def require_subscription(f):
    """Decorator to check if user has active subscription"""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if not eduverse.is_subscription_active(session['user_id']):
            flash('Your trial period has expired. Please subscribe to continue using EduVerse.')
            return redirect(url_for('pricing'))
        
        return f(*args, **kwargs)
    return decorated_function

def require_auth(f):
    """Decorator to check if user is authenticated"""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(limit=10, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' in session:
                user_id = session['user_id']
                current_time = datetime.now()
                
                # Clean old entries
                rate_limit_store = {k: v for k, v in rate_limit_store.items() 
                                  if (current_time - v['timestamp']).seconds < window}
                
                if user_id in rate_limit_store:
                    if rate_limit_store[user_id]['count'] >= limit:
                        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
                    rate_limit_store[user_id]['count'] += 1
                else:
                    rate_limit_store[user_id] = {'count': 1, 'timestamp': current_time}
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user's flashcards
    flashcards = eduverse.get_user_flashcards(session['user_id'])
    
    # Get user's study statistics
    user_stats = eduverse.get_user_stats(session['user_id'])
    
    # Get subscription info
    subscription = eduverse.get_user_subscription(session['user_id'])
    days_remaining = eduverse.get_days_remaining(session['user_id'])
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         flashcards=flashcards,
                         user_stats=user_stats,
                         subscription=subscription,
                         days_remaining=days_remaining)

@app.route('/generate_flashcards', methods=['GET', 'POST'])
@require_subscription
def generate_flashcards():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        notes = request.form['notes']
        topic = request.form['topic']
        num_cards = int(request.form.get('num_cards', 5))
        
        if not notes.strip():
            flash('Please enter some study notes')
            return render_template('generate_flashcards.html')
        
        # Generate flashcards
        try:
            cards = eduverse.generate_flashcards(notes, num_cards)
            print(f"Generated {len(cards)} flashcards")
            
            if not cards:
                flash('No flashcards were generated. Please try again with different notes.')
                return render_template('generate_flashcards.html')
            
            # Save to database
            if eduverse.save_flashcards(session['user_id'], cards, topic):
                flash(f'Successfully generated and saved {len(cards)} flashcards!')
                return redirect(url_for('study_flashcards', topic=topic))
            else:
                flash('Error saving flashcards to database. Please check your database connection.')
                
        except Exception as e:
            print(f"Error in generate_flashcards route: {e}")
            flash('An error occurred while generating flashcards. Please try again.')
    
    return render_template('generate_flashcards.html')

@app.route('/study_flashcards/<topic>')
@require_subscription
def study_flashcards(topic):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    flashcards = eduverse.get_user_flashcards(session['user_id'], topic)
    
    if not flashcards:
        flash('No flashcards found for this topic')
        return redirect(url_for('dashboard'))
    
    # Start a new study session
    session_id = eduverse.start_study_session(session['user_id'], topic)
    if session_id:
        session['current_study_session'] = session_id
    
    return render_template('study_flashcards.html', 
                         flashcards=flashcards,
                         topic=topic,
                         session_id=session_id)

@app.route('/submit_study_results', methods=['POST'])
def submit_study_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    session_id = data.get('session_id')
    cards_studied = data.get('cards_studied', 0)
    correct_answers = data.get('correct_answers', 0)
    time_minutes = data.get('time_minutes', 0)
    
    if session_id and eduverse.update_study_session(session_id, cards_studied, correct_answers, time_minutes):
        # Clear the session from session storage
        session.pop('current_study_session', None)
        return jsonify({'success': True, 'message': 'Study session completed!'})
    else:
        return jsonify({'error': 'Failed to save study results'}), 500

@app.route('/edit_flashcard/<int:flashcard_id>', methods=['GET', 'POST'])
@require_subscription
def edit_flashcard(flashcard_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        topic = request.form['topic']
        difficulty = request.form.get('difficulty', 'medium')
        question_type = request.form.get('question_type', 'short_answer')
        
        if not question.strip() or not answer.strip():
            flash('Question and answer cannot be empty')
            return redirect(url_for('edit_flashcard', flashcard_id=flashcard_id))
        
        if eduverse.update_flashcard(flashcard_id, session['user_id'], question, answer, topic, difficulty, question_type):
            flash('Flashcard updated successfully!')
            return redirect(url_for('dashboard'))
        else:
            flash('Error updating flashcard')
    
    # Get flashcard data for editing
    flashcard = eduverse.get_flashcard_by_id(flashcard_id, session['user_id'])
    if not flashcard:
        flash('Flashcard not found')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_flashcard.html', flashcard=flashcard)

@app.route('/delete_flashcard/<int:flashcard_id>', methods=['POST'])
@require_subscription
def delete_flashcard(flashcard_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if eduverse.delete_flashcard(flashcard_id, session['user_id']):
        return jsonify({'success': True, 'message': 'Flashcard deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete flashcard'}), 500

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', 
                         intasend_publishable_key=INTASEND_PUBLISHABLE_KEY)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if not intasend_service:
        return jsonify({'error': 'Payment service not configured. Please contact support.'}), 500
    
    try:
        # Create IntaSend payment request
        amount = 12.00  # $12 subscription
        currency = "USD"
        
        # Generate unique reference
        reference = f"eduverse_sub_{session['user_id']}_{int(datetime.now().timestamp())}"
        
        # Create payment request using the older API
        payment_data = {
            "first_name": session.get('username', 'User'),
            "last_name": "",
            "email": session.get('email', ''),
            "host": request.host_url,
            "amount": amount,
            "currency": currency,
            "api_ref": reference,
            "redirect_url": url_for('payment_success', _external=True),
            "comment": "EduVerse Premium Subscription"
        }
        
        # Try different API patterns for older versions
        if hasattr(intasend_service, 'collect') and hasattr(intasend_service.collect, 'checkout'):
            response = intasend_service.collect.checkout(**payment_data)
        elif hasattr(intasend_service, 'checkout'):
            response = intasend_service.checkout(**payment_data)
        else:
            return jsonify({'error': 'Payment API not available in this version'}), 500
        
        if response and 'url' in response:
            return jsonify({'success': True, 'payment_url': response['url']})
        else:
            return jsonify({'error': 'Failed to create payment request'}), 500
            
    except Exception as e:
        print(f"Payment error: {e}")
        return jsonify({'error': 'Payment service error'}), 500

@app.route('/payment/success')
def payment_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get payment details from query parameters
    payment_id = request.args.get('id')
    amount = request.args.get('amount', 12.00)
    
    if payment_id:
        # Upgrade user to premium
        if eduverse.upgrade_to_premium(session['user_id'], payment_id, float(amount)):
            flash('Payment successful! Welcome to EduVerse Premium!')
        else:
            flash('Payment received but subscription update failed. Please contact support.')
    else:
        flash('Payment verification failed. Please contact support.')
    
    return redirect(url_for('dashboard'))

@app.route('/payment/cancel')
def payment_cancel():
    flash('Payment was cancelled. You can try again anytime.')
    return redirect(url_for('pricing'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/api/flashcards/<topic>')
def api_flashcards(topic):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    flashcards = eduverse.get_user_flashcards(session['user_id'], topic)
    return jsonify(flashcards)

@app.route('/debug/environment')
def debug_environment():
    """Debug route to check environment variables"""
    return jsonify({
        'google_client_id_set': bool(GOOGLE_CLIENT_ID),
        'google_client_secret_set': bool(GOOGLE_CLIENT_SECRET),
        'github_client_id_set': bool(GITHUB_CLIENT_ID),
        'github_client_secret_set': bool(GITHUB_CLIENT_SECRET),
        'google_oauth_registered': 'google' in oauth._clients,
        'github_oauth_registered': 'github' in oauth._clients,
        'all_env_vars': {
            'GOOGLE_CLIENT_ID': 'SET' if GOOGLE_CLIENT_ID else 'NOT SET',
            'GOOGLE_CLIENT_SECRET': 'SET' if GOOGLE_CLIENT_SECRET else 'NOT SET',
            'GITHUB_CLIENT_ID': 'SET' if GITHUB_CLIENT_ID else 'NOT SET',
            'GITHUB_CLIENT_SECRET': 'SET' if GITHUB_CLIENT_SECRET else 'NOT SET',
        }
    })

@app.route('/debug/database')
def debug_database():
    """Debug route to check database status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db_status = eduverse.test_database_connection()
    db_available = eduverse.db_available
    
    return jsonify({
        'database_available': db_available,
        'connection_test': db_status[0],
        'connection_message': db_status[1],
        'user_id': session['user_id']
    })

def cleanup_expired_data():
    """Clean up expired data on startup"""
    try:
        # This function can be implemented later to clean up expired sessions, etc.
        pass
    except Exception as e:
        print(f"Cleanup error: {e}")

if __name__ == '__main__':
    print("Starting EduVerse application...")
    try:
        # Clean up expired data on startup
        cleanup_expired_data()
        print("Cleanup completed")
    except Exception as e:
        print(f"Warning: Cleanup failed: {e}")
    
    # Use Railway's PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    print("Health check endpoint available at /health")
    
    try:
        app.run(debug=False, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Fatal error starting app: {e}")
        exit(1)
