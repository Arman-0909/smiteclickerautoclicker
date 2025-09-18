import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import Qt
from main_window import MainWindow

class FontManager:
    """A singleton to hold the master, antialiased font."""
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FontManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.antialiased_font = QFont() # Default fallback
            self._load_fonts()
            self._initialized = True

    def _load_fonts(self):
        fonts_path = os.path.join(os.path.dirname(__file__), 'resources', 'fonts')
        regular_font_path = os.path.join(fonts_path, 'Poppins-Regular.ttf')
        semibold_font_path = os.path.join(fonts_path, 'Poppins-SemiBold.ttf')

        regular_font_id = -1
        if os.path.exists(regular_font_path):
            regular_font_id = QFontDatabase.addApplicationFont(regular_font_path)
        else:
            print(f"Warning: Font not found at {regular_font_path}")

        if os.path.exists(semibold_font_path):
            QFontDatabase.addApplicationFont(semibold_font_path)
        else:
            print(f"Warning: Font not found at {semibold_font_path}")

        if regular_font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(regular_font_id)
            if font_families:
                font_family_name = font_families[0]
                self.antialiased_font = QFont(font_family_name, 9)
                self.antialiased_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Smite AutoClicker")
    
    font_manager = FontManager()
    app.setFont(font_manager.antialiased_font)

    window = MainWindow(font_manager)
    window.show()
    sys.exit(app.exec())
