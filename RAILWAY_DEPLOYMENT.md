# 🚀 EduVerse Railway Deployment Guide

## **Prerequisites**
- [Railway Account](https://railway.app/) (Free tier available)
- [GitHub Account](https://github.com/) (for code hosting)
- [MySQL Database](https://planetscale.com/) (free tier available)

## **Step 1: Prepare Your Code**

### **1.1 Push to GitHub**
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial EduVerse commit"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/eduverse.git
git branch -M main
git push -u origin main
```

### **1.2 Verify Files**
Ensure these files are in your repository:
- ✅ `app.py` - Main Flask application
- ✅ `requirements.txt` - Python dependencies
- ✅ `railway.json` - Railway configuration
- ✅ `Procfile` - Alternative deployment config

## **Step 2: Set Up Railway Project**

### **2.1 Create Railway Project**
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `eduverse` repository
5. Click **"Deploy"**

### **2.2 Add MySQL Database**
1. In your Railway project, click **"New"**
2. Select **"Database"** → **"MySQL"**
3. Wait for database to be created
4. Copy the connection details

## **Step 3: Configure Environment Variables**

### **3.1 Database Variables**
In Railway project → Variables tab, add:
```
DB_HOST=your-mysql-host
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=eduverse
```

### **3.2 Flask Variables**
```
SECRET_KEY=generate-random-secret-key
FLASK_ENV=production
```

### **3.3 Email Variables**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

### **3.4 AI & OAuth Variables**
```
HF_API_URL=https://api-inference.huggingface.co/models/deepset/roberta-base-squad2
HF_API_TOKEN=your-huggingface-token
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### **3.5 Payment Variables**
```
INTASEND_PUBLISHABLE_KEY=your-intasend-publishable-key
INTASEND_SECRET_KEY=your-intasend-secret-key
INTASEND_TEST_MODE=False
```

## **Step 4: Deploy**

### **4.1 Automatic Deployment**
- Railway automatically deploys when you push to GitHub
- Check the **Deployments** tab for status

### **4.2 Manual Deployment**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to project
railway link

# Deploy
railway up
```

## **Step 5: Configure Domains**

### **5.1 Custom Domain (Optional)**
1. In Railway project → **Settings** tab
2. Click **"Generate Domain"** or add custom domain
3. Update OAuth callback URLs in Google/GitHub settings

### **5.2 OAuth Callback URLs**
Update your OAuth providers with:
- **Google**: `https://your-domain.railway.app/auth/google/callback`
- **GitHub**: `https://your-domain.railway.app/auth/github/callback`

## **Step 6: Test Deployment**

### **6.1 Health Check**
- Visit your Railway domain
- Check if the app loads correctly
- Test user registration and login

### **6.2 Database Check**
- Verify database tables are created
- Test flashcard generation
- Check subscription system

## **Troubleshooting**

### **Common Issues**

#### **Build Failures**
- Check `requirements.txt` for missing dependencies
- Verify Python version compatibility
- Check build logs in Railway dashboard

#### **Database Connection Errors**
- Verify environment variables are correct
- Check database is running in Railway
- Ensure database credentials are valid

#### **OAuth Errors**
- Update callback URLs in OAuth provider settings
- Verify environment variables are set
- Check Railway domain is correct

#### **Payment Gateway Issues**
- Verify IntaSend credentials
- Check `INTASEND_TEST_MODE` setting
- Ensure proper error handling in logs

## **Monitoring & Maintenance**

### **7.1 Railway Dashboard**
- Monitor app performance
- Check deployment logs
- View resource usage

### **7.2 Database Management**
- Monitor database performance
- Backup data regularly
- Scale resources as needed

### **7.3 Updates**
- Push changes to GitHub
- Railway auto-deploys updates
- Monitor deployment status

## **Success! 🎉**

Your EduVerse app is now deployed on Railway with:
- ✅ **Production-ready Flask app**
- ✅ **MySQL database integration**
- ✅ **OAuth authentication**
- ✅ **Payment gateway integration**
- ✅ **Auto-scaling infrastructure**
- ✅ **Professional domain**

## **Next Steps**
1. **Test all features** on production
2. **Set up monitoring** and alerts
3. **Configure backups** for database
4. **Set up custom domain** (optional)
5. **Monitor performance** and scale as needed

---

**Need Help?** Check Railway documentation or create an issue in your GitHub repository.
