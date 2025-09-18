from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, 
                             QPushButton, QFrame, QApplication, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from ui.custom_widgets import CustomRadioButton # <-- THE FIX: Corrected import path
from ui.layout_widgets import GroupFrame

def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

class LocationPickerOverlay(QWidget):
    location_picked = pyqtSignal(int, int)
    def __init__(self):
        super().__init__(); self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint); self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); self.setCursor(Qt.CursorShape.CrossCursor); screen_geometry = QApplication.primaryScreen().geometry(); self.setGeometry(screen_geometry); self.info_label = QLabel("Click anywhere to select coordinates\nPress Esc to cancel", self); self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.info_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7); color: white; font-size: 20pt; border-radius: 10px;"); layout = QVBoxLayout(self); layout.addStretch(); layout.addWidget(self.info_label); layout.addStretch()
    def mousePressEvent(self, event): pos = event.globalPosition().toPoint(); self.location_picked.emit(pos.x(), pos.y()); self.close()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape: self.close()

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
        self.current_pos_radio.toggled.connect(self.on_target_mode_change)
        
        apply_font_smoothing(self, self.font_manager.antialiased_font)

    def pick_location(self): self.main_window.hide(); QTimer.singleShot(100, self.show_overlay)
    def show_overlay(self): self.picker_overlay = LocationPickerOverlay(); self.picker_overlay.location_picked.connect(self.on_location_picked); self.picker_overlay.show()
    def on_location_picked(self, x, y): self.state_manager.update_setting('specific_pos_x', x); self.state_manager.update_setting('specific_pos_y', y); self.picker_overlay = None; self.main_window.show()
    def on_target_mode_change(self, checked):
        is_specific = self.specific_pos_radio.isChecked(); self.coordinate_input_widget.setEnabled(is_specific); mode = 'specific_pos' if is_specific else 'current_pos'
        if self.state_manager.get_settings()['target_mode'] != mode: self.state_manager.update_setting('target_mode', mode)
    def update_ui_from_state(self):
        settings = self.state_manager.get_settings(); is_specific = settings['target_mode'] == 'specific_pos'
        self.current_pos_radio.toggled.disconnect(self.on_target_mode_change)
        self.specific_pos_radio.setChecked(is_specific); self.current_pos_radio.setChecked(not is_specific)
        self.current_pos_radio.toggled.connect(self.on_target_mode_change)
        self.coordinate_input_widget.setEnabled(is_specific); self.pos_x_spinbox.setValue(settings['specific_pos_x']); self.pos_y_spinbox.setValue(settings['specific_pos_y'])