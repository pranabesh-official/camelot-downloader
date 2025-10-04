# Camelot Downloader

A simple, open-source YouTube music downloader built with Electron, React, and Python. Download your favorite music from YouTube with ease.

## 🎵 Features

- **YouTube Music Download**: Download music directly from YouTube
- **High Quality Audio**: Support for various audio formats and quality levels
- **Cross-Platform**: Built with Electron for Windows, macOS, and Linux
- **Python Backend**: Robust download engine built with Python
- **React Frontend**: Modern, responsive user interface
- **Local Storage**: All downloads stored locally on your device
- **Batch Downloads**: Download multiple tracks at once
- **Progress Tracking**: Real-time download progress and status

## 🎯 Why Use Camelot Downloader?

Camelot Downloader provides a simple, clean interface for downloading music from YouTube without the complexity of music analysis tools. It's perfect for:

- Building your personal music collection
- Downloading music for offline listening
- Getting high-quality audio files from YouTube
- Organizing your downloaded music library

## 🏗️ Architecture

This application uses a simple architecture:
- **Frontend**: React + TypeScript with modern UI components
- **Backend**: Python Flask with YouTube download capabilities
- **Desktop**: Electron for cross-platform compatibility
- **Storage**: Local file system for downloaded music

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v14 or higher)
- **Python 3.8+** (Anaconda recommended)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/camelot-downloader.git
   cd camelot-downloader
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   npm rebuild
   ```

3. **Set up Python environment**
   ```bash
   # On Windows, use cmd instead of PowerShell
   conda env create -f environment.yml
   conda activate camelotdj
   
   # Or use pip directly
   pip install -r requirements.txt
   ```

4. **Start the application**
   ```bash
   # Start the development server
   npm run start
   ```

5. **Start the development server**
   ```bash
   npm run start
   ```

## 🔧 Configuration

### Download Setup

The application is ready to use out of the box:

- **No configuration required** - Just start downloading
- **Choose download location** - Set your preferred download folder
- **Privacy-focused** - All downloads stay on your device
- **Simple interface** - Clean, easy-to-use design

All your downloaded music is stored locally in your chosen directory.

## 🚨 Troubleshooting

### Common Issues

#### 1. **Application Won't Start**
If the application fails to start:
```bash
# Check if all dependencies are installed
npm install

# Restart the development server
npm run start
```

#### 2. **Port Conflicts**
If you see "Something is already running on port 3001":
```bash
# Check what's using port 3001
lsof -i :3001

# Kill conflicting processes
pkill -f "react-scripts"
pkill -f "craco"

# Or use a different port
PORT=3002 npm run start
```

#### 3. **Blank Screen in Production Build**
If the app shows a blank screen after building:
```bash
# Clean and rebuild
npm run build
npm run main-build

# Check the console for build directory errors
# Ensure all build files are properly unpacked
```

#### 4. **Python Backend Issues**
If the Python backend fails to start:
```bash
# Check Python environment
conda activate camelotdj
python --version

# Install missing dependencies
pip install -r requirements.txt

# Test Python API directly
cd python
python api.py --apiport 5002 --signingkey devkey
```

### Local Database

The application uses a local SQLite database that's automatically created when you first run the app. No configuration needed!

## 🏗️ Development

### Available Scripts

```bash
# Development
npm run start          # Start both React and Electron
npm run react-start    # Start only React development server
npm run main-start     # Start only Electron main process
npm run dev            # Start Python backend + React

# Building
npm run build          # Build React app
npm run python-build   # Build Python backend
npm run main-build     # Build Electron app
npm run build:mac      # Build for macOS

# Linting
npm run lint           # Lint all code
npm run react-lint     # Lint React code
npm run main-lint      # Lint Electron code
```

### Project Structure

```
camelot-downloader/
├── main/              # Electron main process
│   ├── index.ts      # Main process entry point
│   └── with-python.ts # Python integration
├── src/               # React frontend
│   ├── components/    # React components
│   ├── services/      # Firebase and API services
│   ├── firebase.ts    # Firebase configuration
│   └── App.tsx        # Main React app
├── python/            # Python backend
│   ├── api.py         # FastAPI server
│   ├── music_analyzer.py # Audio analysis engine
│   └── calc.py        # Key detection algorithms
├── build/             # React build output
├── buildMain/         # Electron build output
├── pythondist/        # Python build output
├── .env.local         # Environment variables (not in git)
├── env.example        # Environment variables template
└── package.json       # Project configuration
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BROWSER` | Browser setting for development | ❌ |
| `REACT_APP_IS_ELECTRON` | Electron mode flag | ❌ |

**Note**: No environment variables are required for basic functionality. The app works out of the box!

## 🎧 How It Works

1. **Search**: Enter a YouTube URL or search for music
2. **Select Quality**: Choose your preferred audio quality and format
3. **Download**: Click download and watch the progress
4. **Organize**: Downloaded files are automatically organized in your chosen folder
5. **Enjoy**: Play your downloaded music with any media player

## 🎵 Download Features

### Quality Options
- Multiple audio quality levels (128kbps to 320kbps)
- Various format support (MP3, M4A, etc.)
- Automatic quality detection and selection

### Batch Processing
- Download multiple tracks simultaneously
- Queue management for large downloads
- Progress tracking for each download

### Organization
- Automatic file naming and organization
- Metadata extraction and tagging
- Custom download folder selection

## 🛠️ Development

### Testing the Python Backend
```bash
cd python
python3 api.py --apiport 5000 --signingkey devkey
```

Visit `http://127.0.0.1:5000/graphiql/` for the GraphQL interface.

### Building for Distribution
```bash
npm run build
```

This creates a packaged application with:
- Python backend compiled with PyInstaller
- React frontend built and optimized
- Platform-specific installer in `dist/`

## 🐛 Troubleshooting

### Common Issues

1. **OpenSSL Error (Node.js 17+)**
   ```bash
   export NODE_OPTIONS="--openssl-legacy-provider"
   npm run start
   ```

2. **Python Dependencies Missing**
   ```bash
   pip3 install flask flask-cors yt-dlp
   ```

3. **Database Issues**
   - The local database is created automatically
   - If you have issues, try deleting the database file and restarting

4. **Port 5000 in Use**
   - Backend will automatically find an available port
   - Or manually specify: `python3 api.py --apiport 5001`

## 🌟 Why Open Source?

We believe that simple, effective tools should be accessible to everyone. Camelot Downloader provides a clean, ad-free alternative to online downloaders with better privacy and control over your downloads.

## 🤝 Contributing

We welcome contributions! This is a simple, focused project and we'd love your help to make it even better.

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly: `npm run lint && npm run build`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## 🙏 Acknowledgments

- **Built on**: [electron-python](https://github.com/yoDon/electron-python) boilerplate
- **Download engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Powerful YouTube download library
- Built with Electron, React, and Python
- Simple, focused, and effective

## 🔗 Related Projects

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Command-line YouTube downloader
- [youtube-dl](https://github.com/ytdl-org/youtube-dl) - Original YouTube downloader
- [Electron](https://electronjs.org/) - Cross-platform desktop apps with web technologies

## 📞 Support

If you encounter any issues or have questions, please:

1. **Check the troubleshooting section** above
2. **Check the documentation** in the `docs/` folder
3. **Search existing issues** on GitHub
4. **Create a new issue** with:
   - Detailed error description
   - Console output/logs
   - Steps to reproduce
   - Environment details (OS, Node.js version, Python version)

### Quick Support Checklist

- [ ] Python environment is activated
- [ ] All dependencies are installed (`npm install`)
- [ ] No port conflicts (3001, 5002)
- [ ] Backend server is running (`./start_backend.sh`)
- [ ] Console shows no compilation errors

---

**Ready to download your favorite music? Start the app and paste a YouTube URL!** 🎶

*This project is for educational purposes. Please respect copyright laws and only download content you have the right to download.*
