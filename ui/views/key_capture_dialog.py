from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

class KeyCaptureDialog(QDialog):
    key_captured = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Hotkey")
        self.setFixedSize(300, 150)
        self.setModal(True)
        
        self.setStyleSheet("background-color: #2d2d2d;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.info_label = QLabel("Press any key to set it as the hotkey.\nPress 'Esc' to cancel.")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        self.captured_key_str = None

    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key.Key_Escape:
            self.reject()
            return

        key_str = ""
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
            key_str = f"Key.f{key - Qt.Key.Key_F1 + 1}"
        else:
            text = event.text()
            if text and text.isprintable():
                key_str = text
        
        if key_str:
            self.captured_key_str = key_str
            self.info_label.setText(f"Hotkey set to: {self.captured_key_str}")
            self.accept()
        else:
            self.info_label.setText("Invalid key. Please try another.")