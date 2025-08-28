# P360 Health & Wellness Platform

A comprehensive AI-powered health and wellness platform featuring ChatGPT integration, personalized health recommendations, content generation, and code assistance.

## 🚀 Features

- **AI Health Chat**: Interactive chatbot for health and wellness questions
- **Smart Health Recommendations**: AI-powered personalized health advice based on user data
- **Content Generation**: Automated creation of health articles, tips, and educational content
- **Code Assistant**: AI-powered coding help, debugging, and code reviews
- **Health Tracking**: Track vital signs, exercise, sleep, and wellness metrics
- **Mobile PWA**: Progressive Web App with offline capabilities
- **Real-time Chat**: WebSocket-based real-time communication

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **OpenAI API** - ChatGPT integration for AI features
- **PostgreSQL** - Primary database for user data and conversations
- **Redis** - Caching and background task management
- **SQLAlchemy** - ORM for database operations
- **Celery** - Background task processing

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework
- **Pinia** - State management
- **Socket.IO** - Real-time communication
- **Chart.js** - Data visualization
- **PWA** - Progressive Web App capabilities

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- OpenAI API Key

## 🔧 Installation & Setup

### 1. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your OpenAI API key and other settings
```

### 2. Using Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### 3. Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🌐 API Features

- **Chat API**: Real-time AI conversations
- **Health API**: Personalized recommendations and data tracking
- **Content API**: AI-powered content generation
- **Code API**: Programming assistance and reviews

## 📱 Mobile PWA

- Responsive design for all devices
- Offline functionality
- Install as mobile app
- Native app-like experience
