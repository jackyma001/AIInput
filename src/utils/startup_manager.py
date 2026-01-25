import os
import sys
import winreg
from src.utils.logger import logger

class StartupManager:
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "AIInput"

    @staticmethod
    def get_exec_command():
        # Get the command to run the app
        executable = sys.executable
        script_path = os.path.abspath(sys.modules['__main__'].__file__)
        return f'"{executable}" "{script_path}"'

    @classmethod
    def is_enabled(cls):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, cls.APP_NAME)
            winreg.CloseKey(key)
            return value == cls.get_exec_command()
        except WindowsError:
            return False

    @classmethod
    def enable(cls):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, cls.get_exec_command())
            winreg.CloseKey(key)
            logger.info("Auto-startup enabled in registry.")
            return True
        except Exception as e:
            logger.error(f"Failed to enable auto-startup: {e}")
            return False

    @classmethod
    def disable(cls):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, cls.APP_NAME)
            winreg.CloseKey(key)
            logger.info("Auto-startup disabled in registry.")
            return True
        except WindowsError:
            return True # Already disabled
        except Exception as e:
            logger.error(f"Failed to disable auto-startup: {e}")
            return False
