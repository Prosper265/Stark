# 🚀 Deployment Guide

This guide provides comprehensive instructions for deploying the Malawi Food Policy Simulator in various environments.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM
- **Storage**: 500MB available space
- **Network**: Internet connection for data updates

### Dependencies
- Streamlit 1.28.0+
- Pandas 2.0.0+
- NumPy 1.24.0+
- Plotly 5.15.0+

## 🏠 Local Development

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd malawi-food-policy-simulator

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Development Server
```bash
# Run with custom port
streamlit run app.py --server.port 8502

# Run with custom host
streamlit run app.py --server.address 0.0.0.0

# Run with debug mode
streamlit run app.py --logger.level debug
```

### Environment Variables
```bash
# Set environment variables
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## ☁️ Cloud Deployment

### Streamlit Cloud (Recommended)

#### Setup
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository and branch
   - Set app URL

3. **Configure Deployment**
   ```toml
   # .streamlit/config.toml
   [server]
   port = 8501
   address = "0.0.0.0"
   
   [browser]
   gatherUsageStats = false
   ```

#### Advanced Configuration
```toml
# .streamlit/config.toml
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#74c69d"
backgroundColor = "#d8f3dc"
secondaryBackgroundColor = "#f0fff4"
textColor = "#123024"
```

### Heroku

#### Setup
1. **Create Heroku App**
   ```bash
   heroku create malawi-food-simulator
   ```

2. **Create Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
   ```

3. **Create runtime.txt**
   ```bash
   echo "python-3.9.16" > runtime.txt
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

#### Heroku Configuration
```bash
# Set environment variables
heroku config:set STREAMLIT_SERVER_PORT=8501
heroku config:set STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Scale application
heroku ps:scale web=1
```

### AWS EC2

#### Instance Setup
1. **Launch EC2 Instance**
   - AMI: Ubuntu 20.04 LTS
   - Instance Type: t3.medium or larger
   - Security Group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python
   sudo apt install python3-pip python3-venv -y
   
   # Install Node.js (for Streamlit)
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd malawi-food-policy-simulator
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run application
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   ```

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/malawi-simulator
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Google Cloud Platform

#### App Engine
1. **Create app.yaml**
   ```yaml
   runtime: python39
   
   env_variables:
     STREAMLIT_SERVER_PORT: 8080
     STREAMLIT_SERVER_ADDRESS: 0.0.0.0
   
   handlers:
   - url: /.*
     script: auto
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

#### Cloud Run
1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8080
   
   CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
   ```

2. **Deploy**
   ```bash
   gcloud run deploy --source .
   ```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  malawi-simulator:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Build and Run
```bash
# Build image
docker build -t malawi-food-simulator .

# Run container
docker run -p 8501:8501 malawi-food-simulator

# Run with docker-compose
docker-compose up -d
```

## 🔒 Security Configuration

### SSL/TLS Setup
```nginx
# Nginx SSL configuration
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        # ... proxy configuration
    }
}
```

### Environment Security
```bash
# Secure environment variables
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
```

### Firewall Configuration
```bash
# UFW firewall rules
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 📊 Monitoring and Logging

### Application Monitoring
```python
# Add to app.py
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Monitoring
```python
# Add performance tracking
import time

@st.cache_data
def load_data():
    start_time = time.time()
    # ... data loading
    end_time = time.time()
    logging.info(f"Data loaded in {end_time - start_time:.2f} seconds")
```

### Health Checks
```python
# Add health check endpoint
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Deploy to Streamlit Cloud
      run: |
        # Deployment commands
```

### Automated Testing
```python
# tests/test_app.py
import pytest
import streamlit as st
from app import load_data, preprocess_data

def test_data_loading():
    """Test data loading functionality"""
    food_comp, consumption, adequacy_df, gender_df, simulations_df = load_data()
    assert not food_comp.empty
    assert not consumption.empty

def test_data_preprocessing():
    """Test data preprocessing"""
    food_comp, consumption, adequacy_df, gender_df, simulations_df = load_data()
    processed_food, processed_consumption, nutrients = preprocess_data(food_comp, consumption)
    assert len(nutrients) > 0
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>
```

#### Memory Issues
```bash
# Increase memory limit
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
```

#### Data Loading Errors
```python
# Add error handling
try:
    data = load_data()
except Exception as e:
    st.error(f"Data loading failed: {e}")
    st.stop()
```

### Performance Optimization
```python
# Optimize data loading
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    # ... data loading
```

### Debug Mode
```bash
# Run with debug logging
streamlit run app.py --logger.level debug
```

## 📈 Scaling

### Horizontal Scaling
- Load balancer configuration
- Multiple instance deployment
- Session state management

### Vertical Scaling
- Increase memory allocation
- Optimize data processing
- Implement caching strategies

### Database Integration
```python
# Add database support
import sqlite3

def load_data_from_db():
    conn = sqlite3.connect('data.db')
    # ... database queries
```

## 🔄 Maintenance

### Regular Updates
- Dependency updates
- Security patches
- Performance improvements
- Feature enhancements

### Backup Strategy
- Data backup procedures
- Configuration backup
- Code version control

### Monitoring
- Application health checks
- Performance metrics
- Error tracking
- User analytics

---

**Last Updated**: January 2024
**Version**: 1.0
**Maintainer**: Development Team
