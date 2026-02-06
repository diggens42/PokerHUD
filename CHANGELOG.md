# Changelog

All notable changes to PokerHUD will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-20

### Added
- **Core Functionality**
  - Passive OCR-based table reading using Tesseract
  - Multi-table support (up to 10 concurrent tables)
  - Real-time transparent HUD overlays
  - SQLite database for persistent player statistics

- **Statistics**
  - VPIP (Voluntarily Put $ In Pot %)
  - PFR (Pre-Flop Raise %)
  - AF (Aggression Factor)
  - 3-Bet Percentage
  - Fold-to-C-Bet Percentage
  - Player style classification (TAG, LAG, Nit, Fish, Reg)

- **User Interface**
  - System tray integration with start/stop controls
  - Settings dialog with persistent JSON configuration
  - First-run welcome dialog with setup instructions
  - Right-click context menu for player notes
  - Note indicator (📝) on HUD displays

- **Features**
  - Session management across multiple tables
  - Hand tracking with street detection
  - Action recognition (fold, call, raise, bet, check)
  - Position-aware stat display
  - Stats caching for performance

- **Configuration**
  - Adjustable HUD opacity and font size
  - Configurable stat thresholds for color-coding
  - Custom Tesseract path configuration
  - Debug mode with screenshot capture
  - Max concurrent tables setting

- **Error Handling**
  - Tesseract availability check with user-friendly messages
  - Database integrity validation with automatic backup
  - OCR failure retry logic
  - Graceful recovery from capture errors
  - Comprehensive logging system

- **Packaging & Distribution**
  - PyInstaller configuration for Windows executable
  - Build documentation and scripts
  - Requirements files for dependencies

### Technical Details
- Built with Python 3.11+
- PyQt6 for GUI and overlays
- Tesseract OCR via pytesseract
- OpenCV and Pillow for image preprocessing
- mss for fast screen capture
- pywin32 for Windows API integration
- SQLite for data persistence

### Documentation
- Comprehensive README with usage instructions
- BUILD.md with packaging guidelines
- Inline code documentation and type hints
- Unit and integration test suite

### Known Issues
- OCR accuracy depends on PokerStars theme and window scaling
- First few hands may have incomplete data
- Stats become reliable after 50+ hands per player

---

## [Unreleased]

### Planned for 1.1.0
- [ ] Support for 888poker
- [ ] Tournament-specific statistics
- [ ] Session review and analysis tool
- [ ] Hand replayer
- [ ] Stats export to CSV/Excel
- [ ] Additional statistics (CBet%, Check-Raise%, Steal%)

### Under Consideration
- [ ] Multi-site support (partypoker, GGPoker)
- [ ] Hand range visualization
- [ ] Cloud synchronization
- [ ] Mobile companion app
- [ ] Advanced analytics dashboard
- [ ] Table heat maps
- [ ] Player search functionality
- [ ] Custom stat profiles

---

## Release Notes

### Version 1.0.0 Release Notes

**PokerHUD 1.0.0** is the initial stable release of our passive OCR-based poker tracking tool. This release includes:

**For Players**:
- Easy-to-use system tray application
- Non-intrusive transparent overlays
- Essential poker statistics at a glance
- Personal note-taking for opponents
- Configurable appearance and behavior

**For Developers**:
- Clean modular architecture
- Comprehensive test coverage
- Type-hinted codebase
- Extensible plugin system foundation
- Well-documented APIs

**Installation**: Download `PokerHUD.exe` from the releases page or build from source.

**First-Time Setup**: 
1. Install Tesseract OCR
2. Launch PokerHUD
3. Follow welcome wizard
4. Configure settings
5. Start tracking!

**Feedback**: Please report bugs and feature requests via GitHub Issues.

---

[1.0.0]: https://github.com/diggens42/PokerHUD/releases/tag/v1.0.0
