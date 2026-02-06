"""First-run experience dialog."""
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class WelcomeDialog(QDialog):
    """Welcome dialog shown on first run."""

    def __init__(self):
        """Initialize welcome dialog."""
        super().__init__()
        self.setWindowTitle("Welcome to PokerHUD")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Welcome to PokerHUD!")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Welcome text
        welcome_text = QTextEdit()
        welcome_text.setReadOnly(True)
        welcome_text.setHtml("""
            <h3>Passive OCR-Based Poker Statistics Tracker</h3>
            
            <p><b>PokerHUD</b> is a completely passive HUD that reads the PokerStars client 
            using OCR (Optical Character Recognition) to track player statistics.</p>
            
            <h4>Features:</h4>
            <ul>
                <li><b>Passive Tracking:</b> No memory reading or client modification</li>
                <li><b>Key Statistics:</b> VPIP, PFR, AF, 3-Bet%, Fold-to-CBet%</li>
                <li><b>Multi-Table Support:</b> Track up to 10 tables simultaneously</li>
                <li><b>Transparent Overlay:</b> Non-intrusive HUD display</li>
                <li><b>Session Persistence:</b> Stats saved across sessions</li>
                <li><b>Player Notes:</b> Right-click any player to add notes</li>
            </ul>
            
            <h4>Setup Steps:</h4>
            <ol>
                <li><b>Install Tesseract OCR:</b><br>
                    Download from: <a href="https://github.com/UB-Mannheim/tesseract/wiki">
                    https://github.com/UB-Mannheim/tesseract/wiki</a><br>
                    Install to default location: C:\\Program Files\\Tesseract-OCR\\</li>
                
                <li><b>Configure Settings:</b><br>
                    Click the system tray icon → Settings<br>
                    Set Tesseract path if not auto-detected</li>
                
                <li><b>Start Tracking:</b><br>
                    Open PokerStars tables<br>
                    Click the system tray icon → Start Tracking<br>
                    HUD overlays will appear on detected tables</li>
            </ol>
            
            <h4>Tips:</h4>
            <ul>
                <li>Stats become reliable after 50+ hands per player</li>
                <li>Right-click any stat display to add player notes</li>
                <li>Adjust HUD opacity and font size in Settings</li>
                <li>Check logs folder if you encounter issues</li>
            </ul>
            
            <p><b>Note:</b> This tool is for educational purposes. Ensure compliance with 
            PokerStars Terms of Service in your jurisdiction.</p>
        """)
        layout.addWidget(welcome_text)
        
        # Don't show again checkbox
        self.dont_show_checkbox = QCheckBox("Don't show this again")
        layout.addWidget(self.dont_show_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.settings_button = QPushButton("Open Settings")
        self.settings_button.clicked.connect(self.accept)
        button_layout.addWidget(self.settings_button)
        
        self.close_button = QPushButton("Get Started")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def should_show_again(self) -> bool:
        """
        Check if dialog should be shown on next run.

        Returns:
            True if should show again, False otherwise.
        """
        return not self.dont_show_checkbox.isChecked()
