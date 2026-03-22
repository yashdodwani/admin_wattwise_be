#!/bin/bash
# WattWise Admin Portal - Startup Script

echo "🚀 WattWise Admin Portal Backend"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please edit it with your settings."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python -c "from config.database import init_db; init_db()" 2>/dev/null || {
    echo "⚠️  Database initialization skipped (check your DATABASE_URL)"
}

# Run Alembic migraines
echo "🔄 Running database migrations..."
python -m alembic upgrade head || echo "⚠️  Migration failed!"

# Optional: Seed notifications if requested
if [ "$SEED_NOTIFICATIONS" = "true" ]; then
    echo "🌱 Seeding notifications..."
    python -m scripts.seed_notifications || echo "⚠️  Notification seeding failed!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting server..."
echo "📖 API docs available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python main.py

