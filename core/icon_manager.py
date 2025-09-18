import os
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QSize, Qt

class IconManager:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance: cls._instance = super(IconManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.base_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons'); self.icon_cache = {}; self._initialized = True
    def get_icon(self, category, name, color="#FFFFFF", size=QSize(22, 22)):
        cache_key = f"{category}_{name}_{color}_{size.width()}x{size.height()}"
        if cache_key in self.icon_cache: return self.icon_cache[cache_key]
        file_path = os.path.join(self.base_path, category, f"{name}.svg")
        if not os.path.exists(file_path): print(f"Warning: Icon not found at {file_path}"); return QIcon()
        with open(file_path, 'r') as f: svg_data = f.read()
        colored_svg_data = svg_data.replace('currentColor', color)
        renderer = QSvgRenderer(colored_svg_data.encode('utf-8'))
        pixmap = QPixmap(size); pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        # --- THE FIX ---
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter); painter.end()
        icon = QIcon(pixmap); self.icon_cache[cache_key] = icon
        return icon