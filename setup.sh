#!/bin/bash

echo "🚀 Setting up P360 Health & Wellness Platform..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your OpenAI API key and database settings"
    echo "   Required: OPENAI_API_KEY, DATABASE_URL, SECRET_KEY"
fi

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "   Installing Python dependencies..."
pip install -r requirements.txt

# Go back to root
cd ..

# Setup frontend
echo "🌐 Setting up Vue.js frontend..."
cd frontend

# Install dependencies
echo "   Installing Node.js dependencies..."
npm install

# Go back to root
cd ..

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Set up PostgreSQL database"
echo "3. Set up Redis server"
echo "4. Run the backend: cd backend && source venv/bin/activate && python start.py"
echo "5. Run the frontend: cd frontend && npm run dev"
echo ""
echo "🌍 URLs:"
echo "   Backend API: http://localhost:8000"
echo "   Frontend App: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🐳 Or use Docker: docker-compose up -d"
