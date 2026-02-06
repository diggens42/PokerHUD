# Build and Distribution Guide

## Prerequisites

### 1. Install PyInstaller
```bash
pip install pyinstaller
```

### 2. Install Tesseract OCR
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- Add to PATH or configure path in settings

## Building the Executable

### One-File Build (Recommended for Distribution)
```bash
pyinstaller PokerHUD.spec
```

The executable will be created in `dist/PokerHUD.exe`.

### Development Build (Faster)
```bash
pyinstaller --onedir main.py --name PokerHUD
```

## Testing the Build

1. **Test on clean machine**: Copy `dist/PokerHUD.exe` to a computer without Python installed
2. **Verify dependencies**: Ensure Tesseract is installed or bundled
3. **Test functionality**:
   - Launch PokerStars client
   - Open practice/play money tables
   - Start PokerHUD
   - Verify table detection
   - Check HUD overlay display
   - Test settings dialog

## Distribution Checklist

- [ ] Executable builds without errors
- [ ] Application launches on clean Windows machine
- [ ] System tray icon appears
- [ ] Settings dialog works
- [ ] Table detection functions
- [ ] HUD overlays display correctly
- [ ] Database creates and persists
- [ ] Stats calculate accurately
- [ ] Player notes save and load
- [ ] Error messages are user-friendly

## Package Size Optimization

Current build excludes:
- matplotlib
- scipy
- pandas
- tkinter
- pytest
- IPython

To further reduce size:
1. Use UPX compression (enabled by default)
2. Remove unused Qt modules
3. Strip debug symbols

## Known Issues

### Issue: Tesseract Not Found
**Solution**: User must install Tesseract separately or bundle it with installer.

### Issue: Antivirus False Positive
**Solution**: Submit to antivirus vendors for whitelisting.

### Issue: Large Executable Size (~150MB)
**Cause**: PyQt6 and OpenCV dependencies.
**Mitigation**: This is normal for GUI+CV applications.

## Creating an Installer (Optional)

Use NSIS or Inno Setup to create a Windows installer:

### Example Inno Setup Script
```iss
[Setup]
AppName=PokerHUD
AppVersion=1.0
DefaultDirName={pf}\PokerHUD
DefaultGroupName=PokerHUD
OutputBaseFilename=PokerHUD_Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\PokerHUD.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\PokerHUD"; Filename: "{app}\PokerHUD.exe"
Name: "{commondesktop}\PokerHUD"; Filename: "{app}\PokerHUD.exe"

[Run]
Filename: "{app}\PokerHUD.exe"; Description: "Launch PokerHUD"; Flags: postinstall nowait skipifsilent
```

## Version Management

Update version in:
1. `config.py` - APP_VERSION
2. `PokerHUD.spec` - version parameter (if added)
3. Installer script
4. README.md

## Release Process

1. Run all tests: `pytest tests/`
2. Update CHANGELOG.md
3. Build executable: `pyinstaller PokerHUD.spec`
4. Test on clean machine
5. Create GitHub release
6. Upload executable
7. Update documentation
