"""
Tray Icon Implementation using PyQt5
Standardized version with clean imports and error handling.
"""
import sys
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt
from src.utils.startup_manager import StartupManager
from src.utils.logger import logger

class TrayIcon:
    def __init__(self, hotkey_manager, listening_bar):
        self.hotkey_manager = hotkey_manager
        self.listening_bar = listening_bar
        self.tray_icon = QSystemTrayIcon()
        self._setup_ui()
        
    def _create_pixmap(self, recording=False):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if recording:
            bg_color = QColor(220, 50, 50)  # Red
        else:
            bg_color = QColor(50, 150, 250)  # Blue
            
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        # White mic body
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(24, 12, 16, 24, 6, 6)
        # Stand simplified
        painter.setPen(QColor(255, 255, 255))
        painter.drawArc(18, 24, 28, 24, 0, 180 * 16)
        
        painter.end()
        return pixmap

    def _setup_ui(self):
        self.tray_icon.setIcon(QIcon(self._create_pixmap(False)))
        self.tray_icon.setToolTip("AIInput - Voice Input (Ctrl+Win)")
        
        menu = QMenu()
        title_action = QAction("AIInput - Voice Input", menu)
        title_action.setEnabled(False)
        menu.addAction(title_action)
        menu.addSeparator()
        
        startup_action = QAction("Run at Startup", menu)
        startup_action.setCheckable(True)
        startup_action.setChecked(StartupManager.is_enabled())
        startup_action.triggered.connect(self._toggle_startup)
        menu.addAction(startup_action)
        
        menu.addSeparator()
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self._on_exit)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def _toggle_startup(self, checked):
        if checked:
            StartupManager.enable()
        else:
            StartupManager.disable()

    def update_status(self, recording=False):
        self.tray_icon.setIcon(QIcon(self._create_pixmap(recording)))
        if recording:
            self.tray_icon.setToolTip("AIInput (Recording...)")
        else:
            self.tray_icon.setToolTip("AIInput - Voice Input (Ctrl+Win)")

    def _on_exit(self):
        logger.info("Application exiting via tray menu.")
        self.hotkey_manager.stop_listening()
        self.tray_icon.hide()
        QApplication.quit()
        sys.exit(0)
