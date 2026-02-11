import os
import sys
from src.utils.logger import logger

class StartupManager:
    APP_NAME = "AIInput"

    @staticmethod
    def get_exec_command():
        # Get the command to run the app
        executable = sys.executable
        script_path = os.path.abspath(sys.modules['__main__'].__file__)
        return f'"{executable}" "{script_path}"'

    @classmethod
    def is_enabled(cls):
        if sys.platform != 'win32':
            return False
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, cls.APP_NAME)
            winreg.CloseKey(key)
            return value == cls.get_exec_command()
        except Exception:
            return False

    @classmethod
    def enable(cls):
        if sys.platform != 'win32':
            logger.info("Auto-startup not implemented for this platform.")
            return False
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, cls.get_exec_command())
            winreg.CloseKey(key)
            logger.info("Auto-startup enabled in registry.")
            return True
        except Exception as e:
            logger.error(f"Failed to enable auto-startup: {e}")
            return False

    @classmethod
    def disable(cls):
        if sys.platform != 'win32':
            return True
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, cls.APP_NAME)
            winreg.CloseKey(key)
            logger.info("Auto-startup disabled in registry.")
            return True
        except Exception:
            return True # Already disabled
