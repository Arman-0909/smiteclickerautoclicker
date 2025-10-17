from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, 
                             QPushButton, QFrame, QApplication, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor
import pygetwindow as gw
from ui.custom_widgets import CustomRadioButton, CustomComboBox, ToggleSwitch
from ui.layout_widgets import GroupFrame

def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

class PixelPerfectPickerOverlay(QWidget):
    location_picked = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.screen = QApplication.primaryScreen()
        self.screenshot = self.screen.grabWindow(0)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.screenshot)
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        painter.setPen(QPen(QColor(255, 255, 255, 150), 1, Qt.PenStyle.DotLine))
        painter.drawLine(cursor_pos.x(), 0, cursor_pos.x(), self.height())
        painter.drawLine(0, cursor_pos.y(), self.width(), cursor_pos.y())
        zoom_factor = 4
        radius = 60
        source_rect_size = int(2 * radius / zoom_factor)
        source_rect = QRect(cursor_pos.x() - source_rect_size // 2, cursor_pos.y() - source_rect_size // 2, source_rect_size, source_rect_size)
        target_rect = QRect(cursor_pos.x() + 20, cursor_pos.y() + 20, 2 * radius, 2 * radius)
        if target_rect.right() > self.width():
            target_rect.moveRight(cursor_pos.x() - 20)
        if target_rect.bottom() > self.height():
            target_rect.moveBottom(cursor_pos.y() - 20)
        magnified_pixmap = self.screenshot.copy(source_rect)
        painter.drawPixmap(target_rect, magnified_pixmap.scaled(target_rect.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.FastTransformation))
        painter.setPen(QPen(QColor("#8A95C1"), 2))
        painter.drawEllipse(target_rect)
        painter.drawLine(target_rect.center().x(), target_rect.top(), target_rect.center().x(), target_rect.bottom())
        painter.drawLine(target_rect.left(), target_rect.center().y(), target_rect.right(), target_rect.center().y())
        info_text = f"X: {cursor_pos.x()}, Y: {cursor_pos.y()}\nClick to select, Esc to cancel"
        painter.setPen(Qt.GlobalColor.white)
        font = painter.font(); font.setPointSize(10); painter.setFont(font)
        text_rect = QRect(target_rect.bottomLeft().x(), target_rect.bottomLeft().y() + 5, 200, 50)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, info_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.globalPosition().toPoint()
            self.location_picked.emit(pos.x(), pos.y())
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape: self.close()

    def mouseMoveEvent(self, event):
        self.update()

class TargetingView(QWidget):
    def __init__(self, state_manager, main_window_instance, font_manager):
        super().__init__(); self.state_manager = state_manager; self.main_window = main_window_instance; self.font_manager = font_manager; self.picker_overlay = None; self.init_ui(); self.state_manager.settings_updated.connect(self.update_ui_from_state); self.update_ui_from_state()

    def init_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0)
        self.card_frame = GroupFrame("Click Targeting"); main_layout.addWidget(self.card_frame)
        self.current_pos_radio = CustomRadioButton("Current Mouse Position"); self.card_frame.content_layout.addWidget(self.current_pos_radio)
        self.specific_pos_radio = CustomRadioButton("Specific Coordinates"); self.card_frame.content_layout.addWidget(self.specific_pos_radio)
        self.coordinate_input_widget = QWidget(); coordinate_input_layout = QHBoxLayout(self.coordinate_input_widget); coordinate_input_layout.setContentsMargins(28, 5, 0, 0)
        self.pos_x_spinbox = QSpinBox(); self.pos_x_spinbox.setRange(0, 9999); self.pos_x_spinbox.valueChanged.connect(lambda v: self.state_manager.update_setting('specific_pos_x', v))
        self.pos_y_spinbox = QSpinBox(); self.pos_y_spinbox.setRange(0, 9999); self.pos_y_spinbox.valueChanged.connect(lambda v: self.state_manager.update_setting('specific_pos_y', v))
        self.pick_location_btn = QPushButton("Pick Location"); self.pick_location_btn.setObjectName("primary_button"); self.pick_location_btn.clicked.connect(self.pick_location)
        coordinate_input_layout.addWidget(QLabel("X:")); coordinate_input_layout.addWidget(self.pos_x_spinbox); coordinate_input_layout.addWidget(QLabel("Y:")); coordinate_input_layout.addWidget(self.pos_y_spinbox); coordinate_input_layout.addStretch(); coordinate_input_layout.addWidget(self.pick_location_btn)
        self.card_frame.content_layout.addWidget(self.coordinate_input_widget)
        self.radio_button_group = QButtonGroup(self); self.radio_button_group.addButton(self.current_pos_radio); self.radio_button_group.addButton(self.specific_pos_radio); self.radio_button_group.setExclusive(True)
        separator = QFrame(); separator.setFrameShape(QFrame.Shape.HLine); separator.setObjectName("separator"); separator.setStyleSheet("border-top: 1px solid rgba(255, 255, 255, 0.05); margin-top: 10px; margin-bottom: 10px;"); self.card_frame.content_layout.addWidget(separator)
        window_toggle_layout = QHBoxLayout(); window_toggle_layout.setContentsMargins(0, 0, 0, 0)
        self.window_toggle_label = QLabel("Target a Specific Window")
        # --- THIS IS THE FIX ---
        # Changed text color from #EAEAEB to #8A95C1
        self.window_toggle_label.setStyleSheet("color: #8A95C1;")
        self.window_targeting_toggle = ToggleSwitch()
        window_toggle_layout.addWidget(self.window_toggle_label); window_toggle_layout.addStretch(); window_toggle_layout.addWidget(self.window_targeting_toggle)
        self.card_frame.content_layout.addLayout(window_toggle_layout)
        self.window_selection_widget = QWidget()
        window_selection_layout = QHBoxLayout(self.window_selection_widget); window_selection_layout.setContentsMargins(0, 5, 0, 0)
        self.window_selector = CustomComboBox()
        self.window_selector.setPlaceholderText("Enable targeting to select window")
        self.refresh_windows_btn = QPushButton("Refresh")
        window_selection_layout.addWidget(self.window_selector); window_selection_layout.addWidget(self.refresh_windows_btn)
        self.card_frame.content_layout.addWidget(self.window_selection_widget)
        self.current_pos_radio.toggled.connect(self.on_target_mode_change); self.specific_pos_radio.toggled.connect(self.on_target_mode_change); self.window_targeting_toggle.toggled.connect(self.on_window_targeting_toggled); self.refresh_windows_btn.clicked.connect(self.populate_windows_list); self.window_selector.currentTextChanged.connect(self.on_window_selected)
        apply_font_smoothing(self, self.font_manager.antialiased_font)

    def on_window_targeting_toggled(self, checked):
        self.state_manager.update_setting('window_targeting_enabled', checked)
        self.window_selection_widget.setEnabled(checked)
        if checked:
            self.populate_windows_list()
        else:
            self.window_selector.setItems([])

    def populate_windows_list(self):
        windows = [title for title in gw.getAllTitles() if title]
        self.window_selector.setItems(windows)

    def on_window_selected(self, window_title):
        self.state_manager.update_setting('target_window', window_title)

    def pick_location(self): self.main_window.hide(); QTimer.singleShot(100, self.show_overlay)
    def show_overlay(self): self.picker_overlay = PixelPerfectPickerOverlay(); self.picker_overlay.location_picked.connect(self.on_location_picked); self.picker_overlay.show()
    def on_location_picked(self, x, y): self.state_manager.update_setting('specific_pos_x', x); self.state_manager.update_setting('specific_pos_y', y); self.picker_overlay = None; self.main_window.show()
    
    def on_target_mode_change(self, checked):
        if not checked: return
        is_specific = self.specific_pos_radio.isChecked()
        self.coordinate_input_widget.setEnabled(is_specific)
        mode = 'specific_pos' if is_specific else 'current_pos'
        if self.state_manager.get_settings()['target_mode'] != mode: self.state_manager.update_setting('target_mode', mode)

    def update_ui_from_state(self):
        settings = self.state_manager.get_settings()
        window_targeting_enabled = settings.get('window_targeting_enabled', False)
        self.window_targeting_toggle.blockSignals(True); self.window_targeting_toggle.setChecked(window_targeting_enabled); self.window_targeting_toggle.blockSignals(False)
        self.window_selection_widget.setEnabled(window_targeting_enabled)
        if window_targeting_enabled:
            current_window = settings.get('target_window')
            if self.window_selector.text() not in self.window_selector.items or not self.window_selector.items:
                 self.populate_windows_list()
            if current_window:
                self.window_selector.setCurrentText(current_window)
        else:
            self.window_selector.setItems([])
        mode = settings.get('target_mode', 'current_pos'); is_specific = mode == 'specific_pos'
        self.specific_pos_radio.blockSignals(True); self.current_pos_radio.blockSignals(True)
        self.specific_pos_radio.setChecked(is_specific); self.current_pos_radio.setChecked(not is_specific)
        self.specific_pos_radio.blockSignals(False); self.current_pos_radio.blockSignals(False)
        self.coordinate_input_widget.setEnabled(is_specific)
        self.pos_x_spinbox.setValue(settings.get('specific_pos_x', 0)); self.pos_y_spinbox.setValue(settings.get('specific_pos_y', 0))