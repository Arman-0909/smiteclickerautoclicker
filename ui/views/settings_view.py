from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from core.hotkey_listener import HotkeyListener
from ui.views.key_capture_dialog import KeyCaptureDialog
from ui.views.warning_dialog import CustomDialog

# New helper function
def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

def create_setting_row(label_text, *widgets):
    row_frame = QFrame(); row_frame.setObjectName("setting_row"); row_layout = QHBoxLayout(row_frame); row_layout.setSpacing(10); label = QLabel(label_text); label.setStyleSheet("font-weight: 500;"); row_layout.addWidget(label, 1)
    for widget in widgets: row_layout.addWidget(widget)
    return row_frame

class SettingsView(QWidget):
    # --- THE FIX: Accept font_manager ---
    def __init__(self, state_manager, font_manager):
        super().__init__()
        self.state_manager = state_manager
        self.font_manager = font_manager # <-- Store font_manager
        self.hotkey_listener = HotkeyListener(self.state_manager); self.hotkey_listener.start()
        self.init_ui()
        self.state_manager.settings_updated.connect(self.update_ui_from_state)
        self.update_ui_from_state()

    def init_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0)
        self.card_frame = QFrame(); self.card_frame.setObjectName("card_frame")
        layout = QVBoxLayout(self.card_frame); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)
        title_label = QLabel("Application Settings"); title_label.setObjectName("title_label"); layout.addWidget(title_label)
        self.start_hotkey_btn = QPushButton(); self.start_hotkey_btn.setToolTip("Click to set the start hotkey."); self.start_hotkey_btn.clicked.connect(lambda: self.capture_key('start'))
        layout.addWidget(create_setting_row("Start Clicking Hotkey", self.start_hotkey_btn))
        self.stop_hotkey_btn = QPushButton(); self.stop_hotkey_btn.setToolTip("Click to set the stop hotkey."); self.stop_hotkey_btn.clicked.connect(lambda: self.capture_key('stop'))
        layout.addWidget(create_setting_row("Stop Clicking Hotkey", self.stop_hotkey_btn))
        layout.addStretch(); main_layout.addWidget(self.card_frame)
        
        # --- THE FIX: Apply font smoothing ---
        apply_font_smoothing(self, self.font_manager.antialiased_font)

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
        self.start_hotkey_btn.setText(settings.get('start_hotkey', 'Not Set').replace('Key.', ''))
        self.stop_hotkey_btn.setText(settings.get('stop_hotkey', 'Not Set').replace('Key.', ''))