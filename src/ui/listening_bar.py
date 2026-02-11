"""
Listening Bar UI - PyQt5 Implementation
Standardized version with clean imports.
"""
import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont
from src.utils.logger import logger

class ListeningBar(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_levels = [0.05] * 50
        self.max_levels = 50
        self.is_recording = False
        self._setup_ui()
        
    def _setup_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.bar_width = 500
        self.bar_height = 70
        self.resize(self.bar_width, self.bar_height)
        
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.bar_width) // 2
        y = screen.height() - self.bar_height - 80
        self.move(x, y)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)
    
    def paintEvent(self, event):
        if not self.isVisible():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(22, 33, 62, 240))
        painter.setPen(QColor(58, 58, 94))
        painter.drawRoundedRect(0, 0, self.bar_width, self.bar_height, 10, 10)
        
        painter.setPen(QColor(233, 69, 96))
        painter.setFont(QFont('Segoe UI', 10, QFont.Bold))
        painter.drawText(0, 5, self.bar_width, 25, Qt.AlignCenter, "🎤 Listening...")
        
        margin = 25
        usable_width = self.bar_width - 2 * margin
        bar_w = usable_width / self.max_levels
        center_y = 45
        
        for i, level in enumerate(self.audio_levels):
            x = margin + i * bar_w
            h = max(6, level * 35)
            g = min(255, int(100 + level * 155))
            painter.setBrush(QColor(0, g, 170))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x+1), int(center_y-h/2), int(bar_w-2), int(h), 2, 2)

    def show_bar(self):
        self.audio_levels = [0.05] * self.max_levels
        # Show window without activating it (keeping focus on the previous app)
        self.show()
        # On macOS, raise_() might still steal focus, let's be careful
        if sys.platform != 'darwin':
            self.raise_()

    def hide_bar(self):
        self.hide()

    def update_audio_level(self, level):
        self.audio_levels.append(level)
        if len(self.audio_levels) > self.max_levels:
            self.audio_levels.pop(0)
