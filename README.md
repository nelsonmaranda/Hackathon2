# 🧠 EduVerse - AI-Powered Learning Platform

> **Transforming Education Through AI Technology**  
> Supporting SDG 4: Quality Education

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

EduVerse is an innovative AI-powered learning platform that transforms study notes into interactive flashcards using advanced machine learning. Built with modern web technologies, it provides an engaging and effective study experience for students worldwide.

### 🎯 Key Features
- **🤖 AI-Powered Flashcard Generation** - Convert notes to smart questions
- **📚 Interactive Study Sessions** - Track progress and performance
- **🔐 Secure User Authentication** - OAuth integration with Google & GitHub
- **💳 Subscription Management** - 7-day trial + premium plans
- **📱 Responsive Design** - Works on all devices
- **🌍 Cloud-Ready** - Deploy anywhere with Railway

## 🚀 Live Demo

(https://eduverseai.up.railway.app/)

## 🏗️ Architecture

### Frontend
- **HTML5 & CSS3** - Modern, responsive design
- **JavaScript** - Interactive user experience
- **Font Awesome** - Beautiful icons and UI elements

### Backend
- **Flask** - Python web framework
- **PyMySQL** - Database connectivity
- **Authlib** - OAuth 2.0 authentication
- **Flask-Mail** - Email verification system

### Database
- **MySQL** - Relational database for user data
- **Schema** - Users, flashcards, study sessions, subscriptions

### AI Integration
- **Hugging Face** - State-of-the-art AI models
- **Question Generation** - Intelligent flashcard creation
- **Fallback System** - Robust error handling

### Payment Gateway
- **IntaSend** - Secure payment processing
- **Subscription Plans** - Trial + premium tiers

## 📋 Prerequisites

Before running EduVerse, ensure you have:

- **Python 3.8+** installed
- **MySQL 8.0+** database server
- **Git** for version control
- **Node.js** (for Railway CLI deployment)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/eduverse.git
cd eduverse
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 5. Database Setup
```sql
-- Create database
CREATE DATABASE eduverse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Database tables will be created automatically on first run
```

### 6. Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` to access EduVerse!

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=eduverse

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password

# Hugging Face AI
HF_API_URL=https://api-inference.huggingface.co/models/deepset/roberta-base-squad2
HF_API_TOKEN=your-huggingface-token

# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# IntaSend Payment Gateway
INTASEND_PUBLISHABLE_KEY=your-intasend-publishable-key
INTASEND_SECRET_KEY=your-intasend-secret-key
INTASEND_TEST_MODE=True
```

### OAuth Setup

#### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:5000/auth/google/callback` (development)
   - `https://your-domain.railway.app/auth/google/callback` (production)

#### GitHub OAuth
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create new OAuth App
3. Add callback URL:
   - `http://localhost:5000/auth/github/callback` (development)
   - `https://your-domain.railway.app/auth/github/callback` (production)

### IntaSend Payment Setup
1. Sign up at [IntaSend](https://intasend.com/)
2. Get your API keys from dashboard
3. Configure webhook endpoints
4. Test payment flow

## 🚀 Railway Deployment

### Quick Deploy
```bash
# Run the quick deploy script
./quick-deploy.bat  # Windows
./quick-deploy.sh   # Linux/Mac
```

### Manual Deployment
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Railway"
   git push
   ```

2. **Create Railway Project**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add MySQL Database**
   - Click "New" → "Database" → "MySQL"
   - Copy connection details

4. **Set Environment Variables**
   - Copy from `railway.env` template
   - Update with your actual values

5. **Deploy**
   - Railway automatically deploys from GitHub
   - Monitor deployment status

### Railway CLI Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

## 📖 Usage Guide

### For Students

#### 1. Getting Started
- **Sign Up** - Create account with email or OAuth
- **7-Day Trial** - Full access to all features
- **Upload Notes** - Paste your study materials

#### 2. Creating Flashcards
- Navigate to "Generate Flashcards"
- Paste your study notes
- AI generates intelligent questions
- Review and edit generated cards
- Save to your personal collection

#### 3. Studying
- Access your flashcard library
- Start study sessions by topic
- Track your progress
- Review performance analytics

#### 4. Subscription
- **Free Trial** - 7 days of full access
- **Premium Plan** - $12/month unlimited access
- **Features** - Advanced AI, unlimited storage, priority support

### For Educators

#### 1. Content Creation
- Generate flashcards from curriculum
- Create topic-based study sets
- Share with students
- Monitor engagement

#### 2. Progress Tracking
- View student performance
- Identify learning gaps
- Adjust content accordingly

## 🔧 Development

### Project Structure
```
eduverse/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── index.html       # Landing page
│   ├── dashboard.html   # User dashboard
│   ├── pricing.html     # Subscription plans
│   └── ...
├── static/              # CSS, JS, assets
├── railway.json         # Railway configuration
├── Procfile            # Alternative deployment
└── README.md           # This file
```

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Flashcards Table
```sql
CREATE TABLE flashcards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    topic VARCHAR(100),
    difficulty ENUM('easy', 'medium', 'hard'),
    question_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### Subscriptions Table
```sql
CREATE TABLE subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    subscription_type ENUM('trial', 'premium'),
    status ENUM('active', 'cancelled', 'expired'),
    trial_start_date DATETIME,
    trial_end_date DATETIME,
    subscription_start_date DATETIME,
    subscription_end_date DATETIME,
    amount_paid DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### API Endpoints

#### Authentication
- `POST /signup` - User registration
- `POST /login` - User authentication
- `GET /logout` - User logout
- `GET /auth/google` - Google OAuth
- `GET /auth/github` - GitHub OAuth

#### Flashcards
- `GET /dashboard` - User dashboard
- `POST /generate_flashcards` - Generate AI flashcards
- `GET /study_flashcards/<topic>` - Study session
- `POST /edit_flashcard/<id>` - Edit flashcard
- `POST /delete_flashcard/<id>` - Delete flashcard

#### Subscriptions
- `GET /pricing` - Subscription plans
- `POST /subscribe` - Create subscription
- `GET /payment/success` - Payment success
- `GET /payment/cancel` - Payment cancellation

## 🧪 Testing

### Local Testing
```bash
# Run the application
python app.py

# Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/dashboard
```

### Feature Testing
1. **User Registration** - Test signup flow
2. **OAuth Integration** - Test Google/GitHub login
3. **Flashcard Generation** - Test AI question creation
4. **Study Sessions** - Test learning flow
5. **Payment System** - Test subscription flow

## 🐛 Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check MySQL service
sudo systemctl status mysql

# Verify credentials
mysql -u username -p -h hostname
```

#### OAuth Errors
- Verify callback URLs match exactly
- Check environment variables
- Ensure OAuth apps are properly configured

#### Payment Issues
- Verify IntaSend credentials
- Check test mode settings
- Review payment logs

#### Build Failures
- Check Python version compatibility
- Verify all dependencies in requirements.txt
- Check Railway build logs

### Debug Routes
```bash
# Database status check
GET /debug/database

# Check environment variables
GET /debug/env
```

## 📊 Performance

### Optimization Features
- **Database Indexing** - Optimized queries
- **Caching** - Session management
- **Lazy Loading** - Efficient data fetching
- **Connection Pooling** - Database optimization

### Monitoring
- **Railway Dashboard** - Performance metrics
- **Database Monitoring** - Query performance
- **Error Logging** - Comprehensive error tracking

## 🔒 Security

### Security Features
- **Password Hashing** - SHA-256 encryption
- **OAuth 2.0** - Secure authentication
- **Session Management** - Secure user sessions
- **SQL Injection Protection** - Parameterized queries
- **HTTPS** - SSL encryption (Railway)

### Best Practices
- Regular security updates
- Environment variable protection
- Input validation and sanitization
- Secure payment processing

## 📈 Scaling

### Railway Scaling
- **Auto-scaling** based on traffic
- **Load balancing** across instances
- **Database scaling** options
- **CDN integration** for static assets

### Performance Optimization
- **Database indexing** strategies
- **Query optimization** techniques
- **Caching strategies** implementation
- **Resource monitoring** and alerts

## 🤝 Contributing

### How to Contribute
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Development Guidelines
- Follow PEP 8 Python style guide
- Add comprehensive tests
- Update documentation
- Maintain backward compatibility

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask** - Web framework
- **Hugging Face** - AI models
- **IntaSend** - Payment processing
- **Railway** - Deployment platform
- **Font Awesome** - Icons and UI elements

## 📞 Support

### Getting Help
- **Documentation** - This README and deployment guide
- **Issues** - GitHub issues for bug reports
- **Discussions** - GitHub discussions for questions
- **Email** - Contact for business inquiries

### Community
- **GitHub** - [Repository](https://github.com/yourusername/eduverse)
- **Discussions** - [GitHub Discussions](https://github.com/yourusername/eduverse/discussions)
- **Issues** - [Bug Reports](https://github.com/yourusername/eduverse/issues)

## 🚀 Roadmap

### Upcoming Features
- [ ] **Mobile App** - iOS and Android applications
- [ ] **Advanced Analytics** - Detailed learning insights
- [ ] **Collaborative Learning** - Group study features
- [ ] **Offline Mode** - Study without internet
- [ ] **API Access** - Third-party integrations
- [ ] **Multi-language Support** - International accessibility

### Version History
- **v1.0.0** - Initial release with core features
- **v1.1.0** - OAuth integration and payment system
- **v1.2.0** - Enhanced AI models and analytics
- **v2.0.0** - Mobile apps and advanced features

---

## 🌟 Star the Project

If EduVerse helps you in your learning journey, please consider giving it a ⭐ on GitHub!

**Made with ❤️ for Quality Education Worldwide**

---

*EduVerse - Transforming Education Through AI Technology*
