# Project Structure

```
amazon_agent/
├── README.md                 # Main documentation
├── INSTALLATION_GUIDE.md    # End user installation instructions
├── DISTRIBUTION_GUIDE.md     # Developer guide for releases
├── PREPARE_RELEASE.md        # Step-by-step release process
├── RELEASE_NOTES.md          # Release notes template
├── CONTRIBUTING.md           # Contribution guidelines
│
├── Core Application Files
│   ├── amazon_fresh_fetch.py # Main Streamlit app entry point
│   ├── agent.py              # LangGraph agent nodes
│   ├── browser.py            # Playwright browser automation
│   ├── database.py           # SQLite database manager
│   ├── config.py             # Configuration constants
│   └── pdf_generator.py       # PDF export functionality
│
├── Installer Files
│   ├── installer.py          # Main installer (standalone, no Git needed)
│   ├── build_standalone.py   # Build standalone installers
│   ├── build_windows.py      # Windows-specific build
│   ├── build_mac.py           # macOS-specific build
│   └── build.sh              # Auto-detect platform build
│
├── Requirements
│   └── requirements.txt      # Python dependencies
│
├── Tests
│   └── tests/                # Unit tests
│
└── Configuration
    ├── .gitignore            # Git ignore rules
    └── .github/
        └── workflows/        # GitHub Actions (optional)
```

## Key Files

### For End Users
- `INSTALLATION_GUIDE.md` - How to install and use the app
- `README.md` - Complete documentation

### For Developers
- `DISTRIBUTION_GUIDE.md` - How to build and distribute
- `PREPARE_RELEASE.md` - Release checklist
- `CONTRIBUTING.md` - How to contribute

### Build Files
- `installer.py` - Main installer script
- `build_standalone.py` - Build standalone executables
- `build_windows.py` - Windows build script
- `build_mac.py` - macOS build script

## Ignored Files (in .gitignore)

- `dist/` - Build output
- `build/` - Build artifacts
- `.venv/` - Virtual environment
- `.env` - Environment variables
- `agent_data.db` - User database
- `user_session/` - Browser session data
- `amazon_session.json` - Amazon session
- `__pycache__/` - Python cache

