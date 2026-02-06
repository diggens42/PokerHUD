# PokerHUD

**Version 1.0.0**

A passive OCR-based poker HUD (Heads-Up Display) for PokerStars that tracks player statistics across sessions without modifying the poker client or reading memory.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## Features

### Core Functionality
- **Passive Tracking**: Uses OCR (Optical Character Recognition) to read table information - no memory reading or client modification
- **Multi-Table Support**: Track up to 10 tables simultaneously
- **Persistent Statistics**: Player stats saved to SQLite database across sessions
- **Real-Time HUD**: Transparent overlay displays stats next to each player

### Statistics Tracked
- **VPIP** (Voluntarily Put $ In Pot %): How often a player enters pots
- **PFR** (Pre-Flop Raise %): How often a player raises preflop
- **AF** (Aggression Factor): Ratio of aggressive to passive actions
- **3-Bet%**: How often a player 3-bets preflop
- **Fold-to-CBet%**: How often a player folds to continuation bets

### User Experience
- **Player Notes**: Right-click any HUD display to add personal notes
- **Configurable Settings**: Adjust HUD appearance, OCR paths, and stat thresholds
- **System Tray Integration**: Convenient start/stop/settings controls
- **Error Handling**: Graceful recovery from OCR failures, missing dependencies
- **Welcome Dialog**: First-run setup wizard

## Screenshots

*(Add screenshots here showing HUD overlay, settings dialog, system tray)*

## Installation

### Prerequisites

1. **Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure "Add to PATH" is checked during installation

2. **Tesseract OCR**
   - Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install to default location: `C:\Program Files\Tesseract-OCR\`
   - Or configure custom path in settings

### Option 1: Binary Release (Recommended for Users)

1. Download `PokerHUD.exe` from [Releases](https://github.com/diggens42/PokerHUD/releases)
2. Run `PokerHUD.exe`
3. Follow welcome dialog instructions
4. Configure Tesseract path in settings if needed

### Option 2: From Source (For Developers)

```bash
# Clone repository
git clone https://github.com/diggens42/PokerHUD.git
cd PokerHUD

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Usage

### Quick Start

1. **Start PokerStars** and open cash game or tournament tables
2. **Launch PokerHUD** - the system tray icon will appear
3. **Start Tracking** via system tray menu
4. **HUD Overlays** will automatically appear on detected tables
5. **View Stats** - stats become reliable after 50+ hands per player

### Adding Player Notes

1. Right-click any player's HUD display
2. Select "Add Note for [Player]"
3. Enter note text
4. Notes are saved and displayed with 📝 indicator

### Configuring Settings

Access via System Tray → Settings:

**General**
- Capture Interval: How often to screenshot tables (default: 500ms)
- Tesseract Path: Location of tesseract.exe
- Debug Mode: Save screenshot captures for troubleshooting
- Max Tables: Maximum concurrent tables to track (1-10)

**HUD Appearance**
- Opacity: Background transparency (0.0-1.0)
- Font Size: Stat display text size (6-20)

**Stat Thresholds**
- VPIP Tight/Loose: Ranges for color-coding player styles
- PFR Tight/Loose: Preflop raise frequency thresholds
- AF Passive/Aggressive: Aggression factor boundaries
- 3-Bet Low/High: 3-betting frequency ranges
- Fold-to-CBet Low/High: C-bet fold frequency ranges

## Architecture

```
PokerHUD/
├── pokerlens/
│   ├── core/           # Screen capture, OCR, table detection
│   ├── parser/         # Hand parsing, action recognition
│   ├── stats/          # Statistics calculation
│   ├── storage/        # Database management
│   ├── overlay/        # HUD windows, system tray, settings
│   └── utils/          # Logging, error handling, image processing
├── tests/              # Unit and integration tests
├── config.py           # Global configuration
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

### Technology Stack

- **GUI**: PyQt6 (transparent overlays, dialogs)
- **OCR**: Tesseract via pytesseract
- **Screen Capture**: mss (fast screenshot library)
- **Image Processing**: OpenCV, Pillow
- **Database**: SQLite
- **Windows API**: pywin32 (window detection)

## Development

### Running Tests

```bash
pytest tests/
```

### Building Executable

```bash
# Install build dependencies
pip install -r requirements-build.txt

# Build with PyInstaller
pyinstaller PokerHUD.spec

# Executable created at: dist/PokerHUD.exe
```

See [BUILD.md](BUILD.md) for detailed build instructions.

### Project Structure

**Core Components**:
- `ScreenCapture`: Fast region-based window capture
- `TableDetector`: Finds PokerStars windows via win32gui
- `OCREngine`: Tesseract wrapper with preprocessing strategies
- `TableStateParser`: Converts OCR reads into structured data
- `HandTracker`: Detects hand boundaries and street transitions
- `StatsCalculator`: Computes poker statistics from hand history
- `Database`: SQLite persistence layer with caching
- `HUDWindow`: Transparent PyQt6 overlay with click-through

### Adding New Statistics

1. Update `pokerlens/stats/calculator.py` with calculation logic
2. Modify `PlayerStats` dataclass in `pokerlens/stats/calculator.py`
3. Update HUD display formatting in `pokerlens/overlay/stat_widget.py`
4. Add database columns/queries as needed in `pokerlens/storage/database.py`

## Troubleshooting

### HUD Not Appearing

- Verify PokerStars tables are open and visible
- Check system tray - ensure "Start Tracking" is active
- Confirm window titles match patterns (contains "Hold'em" or "Omaha")
- Review logs in `logs/` directory

### OCR Errors

- Install/reinstall Tesseract OCR
- Configure correct path in Settings
- Ensure PokerStars client is at 100% Windows scaling
- Try different table themes (darker backgrounds work better)

### Database Corruption

- Application will prompt to backup and recreate
- Manual backup: copy `data/pokerhud.db` before launch
- Restore from backup: replace database file while app is closed

### Performance Issues

- Reduce max concurrent tables in settings
- Increase capture interval (500ms → 1000ms)
- Close other resource-intensive applications
- Disable debug mode (saves captures to disk)

## Legal & Compliance

**Important**: This tool is provided for **educational purposes only**.

- PokerHUD is a **passive tool** that only reads visible screen pixels
- No memory reading, packet sniffing, or client modification occurs
- **You are responsible** for compliance with PokerStars Terms of Service in your jurisdiction
- Some poker sites prohibit **any** third-party software - review their policies
- Use at your own risk - the developers assume no liability

## Contributing

Contributions welcome! Areas for improvement:

- Support for additional poker sites (888, partypoker, etc.)
- More statistics (CBet%, Check-Raise%, Steal%)
- Hand range visualization
- Session graphs and analytics
- Tournament-specific stats (ICM, ROI)
- Multi-language OCR support

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

**Version 1.1** (Planned):
- [ ] 888poker support
- [ ] Tournament HUD mode
- [ ] Session review tool
- [ ] Hand replayer
- [ ] Stats export (CSV/Excel)

**Version 2.0** (Future):
- [ ] Multi-site support
- [ ] Advanced stats dashboard
- [ ] Cloud sync
- [ ] Mobile companion app

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [OpenCV](https://opencv.org/) - Image processing
- PokerStars for poker client (this project is not affiliated with or endorsed by PokerStars)

## Support

- **Issues**: [GitHub Issues](https://github.com/diggens42/PokerHUD/issues)
- **Discussions**: [GitHub Discussions](https://github.com/diggens42/PokerHUD/discussions)
- **Email**: fredericmarcel.wahl@exyte.net

## Changelog

### Version 1.0.0 (2024)
- Initial release
- Multi-table support (up to 10 tables)
- Core stats: VPIP, PFR, AF, 3-Bet%, Fold-to-CBet%
- Player notes system
- Configurable HUD appearance
- System tray integration
- Error handling and recovery
- First-run welcome dialog
- SQLite persistence
- Windows executable distribution

---

**Made with ♥️ for the poker community**

PokerHUD is a Windows-only, passive OCR-based poker HUD for PokerStars. It reads the visible screen using screenshots only, tracks player statistics across sessions, and renders a transparent overlay next to each seat. It never injects into the poker client, never reads memory, and never sends any input.

## Key Features

- Fast screen capture via mss
- OCR using Tesseract with poker-optimized preprocessing
- Local SQLite storage for player stats
- PyQt6 transparent, click-through HUD overlay

## Status

Project scaffold and configuration are in place. Implementation will proceed in small, testable milestones.

## Requirements

- Windows 10/11
- Python 3.11+
- Tesseract OCR installed (configured later)

## Project Structure

```
PokerHUD/
├── pokerlens/
├── resources/
├── tests/
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Safety Constraints

PokerHUD is strictly passive and uses only screen capture. It does not hook, inject, or interact with the poker client in any way.
