# PokerHUD

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
