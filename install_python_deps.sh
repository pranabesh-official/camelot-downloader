#!/bin/bash

echo "🐍 Installing Python dependencies for CAMELOTDJ..."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install pip first."
    exit 1
fi

# Upgrade pip first
echo "📦 Upgrading pip..."
pip3 install --upgrade pip

# Install core dependencies
echo "📦 Installing core Flask dependencies..."
pip3 install flask flask-cors flask-socketio flask-graphql graphene

# Install audio processing libraries
echo "🎵 Installing audio processing libraries..."
pip3 install librosa mutagen pydub scipy numpy pandas

# Install YouTube downloading libraries
echo "📺 Installing YouTube libraries..."
pip3 install ytmusicapi pytube yt-dlp

# Install system utilities
echo "🔧 Installing system utilities..."
pip3 install requests psutil

# Install image processing
echo "🖼️ Installing image processing..."
pip3 install Pillow

# Install AI/ML libraries (optional, for auto-mix features)
echo "🤖 Installing AI libraries..."
pip3 install llm

# Install packaging tools
echo "📦 Installing packaging tools..."
pip3 install pyinstaller

# Try to install essentia (might need special handling)
echo "🎼 Installing Essentia (audio analysis)..."
pip3 install essentia-tensorflow || pip3 install essentia || echo "⚠️ Essentia installation failed - some audio analysis features may not work"

# Install mirdata (music information retrieval)
echo "📊 Installing mirdata..."
pip3 install mirdata || echo "⚠️ mirdata installation failed - some features may not work"

echo "✅ Python dependencies installation completed!"
echo ""
echo "🔍 Verifying installations..."

# Verify key imports
python3 -c "
try:
    import flask
    print('✅ Flask: OK')
except ImportError:
    print('❌ Flask: FAILED')

try:
    import flask_cors
    print('✅ Flask-CORS: OK')
except ImportError:
    print('❌ Flask-CORS: FAILED')

try:
    import flask_socketio
    print('✅ Flask-SocketIO: OK')
except ImportError:
    print('❌ Flask-SocketIO: FAILED')

try:
    import ytmusicapi
    print('✅ YTMusicAPI: OK')
except ImportError:
    print('❌ YTMusicAPI: FAILED')

try:
    import yt_dlp
    print('✅ yt-dlp: OK')
except ImportError:
    print('❌ yt-dlp: FAILED')

try:
    import librosa
    print('✅ librosa: OK')
except ImportError:
    print('❌ librosa: FAILED')

try:
    import mutagen
    print('✅ mutagen: OK')
except ImportError:
    print('❌ mutagen: FAILED')

try:
    import requests
    print('✅ requests: OK')
except ImportError:
    print('❌ requests: FAILED')

try:
    import psutil
    print('✅ psutil: OK')
except ImportError:
    print('❌ psutil: FAILED')
"

echo ""
echo "🎉 Installation verification complete!"
echo "You can now run the application."