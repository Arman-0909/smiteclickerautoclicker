from PyQt6.QtWidgets import (QWidget, QCheckBox, QPushButton, QMenu, QHBoxLayout, 
                             QLabel, QAbstractButton)
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve, pyqtProperty, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QAction
from core.icon_manager import IconManager

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent); self.setCursor(Qt.CursorShape.PointingHandCursor)
        # --- NEW "EXODUS" COLORS ---
        self._track_color_off = QColor("#111111")
        self._track_color_on = QColor("#8A95C1")
        self._thumb_color = QColor("#EAEAEB")
        
        # --- NEW SMALLER SIZE ---
        self.setFixedSize(38, 22)
        self.thumb_radius = 8
        self.padding = 3
        
        self.animation = QPropertyAnimation(self, b"thumb_position", self); self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic); self.animation.setDuration(200); self.thumb_position; self.stateChanged.connect(self._handle_state_change)
    @pyqtProperty(QPoint)
    def thumb_position(self):
        if not hasattr(self, '_thumb_pos'):
            if self.isChecked(): self._thumb_pos = QPoint(self.width() - self.thumb_radius - self.padding, self.height() // 2)
            else: self._thumb_pos = QPoint(self.thumb_radius + self.padding, self.height() // 2)
        return self._thumb_pos
    @thumb_position.setter
    def thumb_position(self, pos): self._thumb_pos = pos; self.update()
    def _handle_state_change(self, state):
        self.animation.setStartValue(self.thumb_position); end_pos = QPoint(self.width() - self.thumb_radius - self.padding, self.height() // 2) if state else QPoint(self.thumb_radius + self.padding, self.height() // 2); self.animation.setEndValue(end_pos); self.animation.start()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw the subtle border
        painter.setPen(QPen(QColor("rgba(255,255,255,0.05)")))
        
        track_color = self._track_color_on if self.isChecked() else self._track_color_off
        track_rect = self.rect()
        painter.setBrush(QBrush(track_color)); painter.drawRoundedRect(track_rect, 11, 11)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._thumb_color))
        painter.drawEllipse(self.thumb_position, self.thumb_radius, self.thumb_radius)
    def mousePressEvent(self, event): self.toggle(); super().mousePressEvent(event)

# ... (The other custom widgets are unchanged) ...
class CustomComboBox(QPushButton):
    currentTextChanged = pyqtSignal(str)
    def __init__(self, items=None, parent=None):
        super().__init__(parent); self.items = items if items else []; self.setObjectName("customComboBox"); self.setCursor(Qt.CursorShape.PointingHandCursor); self.icon_manager = IconManager(); self.menu = QMenu(self); self.menu.setObjectName("customMenu"); self.populate_menu(); self.clicked.connect(self.show_menu)
        if self.items: self.setText(self.items[0])
    def populate_menu(self):
        self.menu.clear()
        for item_text in self.items: action = QAction(item_text, self); action.triggered.connect(lambda checked=False, text=item_text: self.on_item_selected(text)); self.menu.addAction(action)
    def show_menu(self): self.menu.popup(self.mapToGlobal(QPoint(0, self.height())))
    def on_item_selected(self, text): self.setText(text); self.currentTextChanged.emit(text)
    def setText(self, text): super().setText(text)
    def setCurrentText(self, text):
        if text in self.items: self.setText(text)

class CustomRadioButton(QAbstractButton):
    def __init__(self, text="", parent=None):
        super().__init__(parent); self._text = text; self._is_hovered = False; self.setCheckable(True); self.setCursor(Qt.CursorShape.PointingHandCursor); self.setMouseTracking(True); self.setFixedHeight(30)
    def mouseMoveEvent(self, event): self._is_hovered = True; self.update(); super().mouseMoveEvent(event)
    def leaveEvent(self, event): self._is_hovered = False; self.update(); super().leaveEvent(event)
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing); outer_ring_color = QColor("#8A95C1") if self._is_hovered else QColor("#3E3E42"); inner_dot_color = QColor("#8A95C1"); text_color = QColor("#EAEAEB"); indicator_size = 16; indicator_y = (self.height() - indicator_size) // 2; painter.setPen(QPen(outer_ring_color, 2)); painter.setBrush(Qt.BrushStyle.NoBrush); painter.drawEllipse(1, indicator_y, indicator_size, indicator_size)
        if self.isChecked(): painter.setBrush(QBrush(inner_dot_color)); painter.setPen(Qt.PenStyle.NoPen); dot_size = 8; dot_margin = (indicator_size - dot_size) // 2; painter.drawEllipse(1 + dot_margin, indicator_y + dot_margin, dot_size, dot_size)
        painter.setPen(text_color); font = self.font(); painter.setFont(font); text_x = indicator_size + 10; text_y = 0; text_width = self.width() - text_x; text_height = self.height(); painter.drawText(text_x, text_y, text_width, text_height, Qt.AlignmentFlag.AlignVCenter, self._text)