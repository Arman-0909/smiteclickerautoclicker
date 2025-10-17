from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QButtonGroup
from PyQt6.QtCore import Qt

from core.hotkey_listener import HotkeyListener
from ui.views.key_capture_dialog import KeyCaptureDialog
from ui.views.warning_dialog import CustomDialog
from ui.custom_widgets import CustomRadioButton # <-- Import CustomRadioButton

def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

def create_setting_row(label_text, *widgets):
    row_frame = QFrame(); row_frame.setObjectName("setting_row"); row_layout = QHBoxLayout(row_frame); row_layout.setSpacing(10); label = QLabel(label_text); label.setStyleSheet("font-weight: 500;"); row_layout.addWidget(label, 1)
    for widget in widgets: row_layout.addWidget(widget)
    return row_frame

class SettingsView(QWidget):
    def __init__(self, state_manager, font_manager):
        super().__init__()
        self.state_manager = state_manager
        self.font_manager = font_manager
        self.hotkey_listener = HotkeyListener(self.state_manager); self.hotkey_listener.start()
        self.init_ui()
        self.state_manager.settings_updated.connect(self.update_ui_from_state)
        self.update_ui_from_state()

    def init_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0)
        self.card_frame = QFrame(); self.card_frame.setObjectName("card_frame")
        layout = QVBoxLayout(self.card_frame); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)
        title_label = QLabel("Application Settings"); title_label.setObjectName("title_label"); layout.addWidget(title_label)
        
        # --- Hotkey Rows ---
        self.start_hotkey_btn = QPushButton(); self.start_hotkey_btn.setToolTip("Click to set the start hotkey."); self.start_hotkey_btn.clicked.connect(lambda: self.capture_key('start'))
        self.start_hotkey_row = create_setting_row("Activation Hotkey", self.start_hotkey_btn)
        layout.addWidget(self.start_hotkey_row)

        self.stop_hotkey_btn = QPushButton(); self.stop_hotkey_btn.setToolTip("Click to set the stop hotkey."); self.stop_hotkey_btn.clicked.connect(lambda: self.capture_key('stop'))
        self.stop_hotkey_row = create_setting_row("Stop Clicking Hotkey", self.stop_hotkey_btn)
        layout.addWidget(self.stop_hotkey_row)

        # --- NEW UI: Hotkey Mode ---
        separator = QFrame(); separator.setFrameShape(QFrame.Shape.HLine); separator.setObjectName("separator"); separator.setStyleSheet("border-top: 1px solid rgba(255, 255, 255, 0.05); margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(separator)
        
        mode_label = QLabel("Activation Mode"); mode_label.setStyleSheet("font-weight: 500;")
        layout.addWidget(mode_label)
        
        self.toggle_mode_radio = CustomRadioButton("Toggle: Press hotkey to start, press again to stop.")
        self.hold_mode_radio = CustomRadioButton("Hold: Clicking is active only while holding the hotkey.")
        
        self.hotkey_mode_group = QButtonGroup(self)
        self.hotkey_mode_group.addButton(self.toggle_mode_radio)
        self.hotkey_mode_group.addButton(self.hold_mode_radio)

        self.toggle_mode_radio.toggled.connect(self.on_hotkey_mode_changed)
        # We only need to connect one, the group handles the logic.

        layout.addWidget(self.toggle_mode_radio)
        layout.addWidget(self.hold_mode_radio)
        
        layout.addStretch(); main_layout.addWidget(self.card_frame)
        
        apply_font_smoothing(self, self.font_manager.antialiased_font)
    
    def on_hotkey_mode_changed(self, checked):
        # This signal fires for both buttons, we only care about the one being checked ON.
        if not checked:
            return
            
        mode = 'Hold' if self.hold_mode_radio.isChecked() else 'Toggle'
        self.state_manager.update_setting('hotkey_mode', mode)

    def capture_key(self, which_key):
        dialog = KeyCaptureDialog(self)
        if dialog.exec():
            key_str = dialog.captured_key_str
            if key_str: self.set_hotkey(which_key, key_str)

    def set_hotkey(self, which_key, key_str):
        settings = self.state_manager.get_settings()
        if which_key == 'start' and key_str == settings['stop_hotkey']: dialog = CustomDialog("warning", "Conflict", "This key is already used for the stop hotkey.", show_cancel=False, parent=self); dialog.exec()
        elif which_key == 'stop' and key_str == settings['start_hotkey']: dialog = CustomDialog("warning", "Conflict", "This key is already used for the start hotkey.", show_cancel=False, parent=self); dialog.exec()
        else:
            if which_key == 'start': self.state_manager.update_setting('start_hotkey', key_str)
            else: self.state_manager.update_setting('stop_hotkey', key_str)

    def update_ui_from_state(self):
        settings = self.state_manager.get_settings()
        
        # --- Update Hotkey Mode UI ---
        hotkey_mode = settings.get('hotkey_mode', 'Toggle')
        
        self.toggle_mode_radio.blockSignals(True)
        self.hold_mode_radio.blockSignals(True)
        
        if hotkey_mode == 'Hold':
            self.hold_mode_radio.setChecked(True)
            self.stop_hotkey_row.hide() # Hide the stop button in Hold mode
            # Update the label to be more descriptive for both modes
            self.start_hotkey_row.findChild(QLabel).setText("Activation Hotkey")
        else: # Toggle mode
            self.toggle_mode_radio.setChecked(True)
            self.stop_hotkey_row.show() # Show the stop button in Toggle mode
            self.start_hotkey_row.findChild(QLabel).setText("Start Clicking Hotkey")

        self.toggle_mode_radio.blockSignals(False)
        self.hold_mode_radio.blockSignals(False)

        # Update Hotkey Buttons Text
        self.start_hotkey_btn.setText(settings.get('start_hotkey', 'Not Set').replace('Key.', ''))
        self.stop_hotkey_btn.setText(settings.get('stop_hotkey', 'Not Set').replace('Key.', ''))