from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QStyle
from PyQt6.QtCore import Qt, QTimer

class CustomDialog(QDialog):
    def __init__(self, dialog_type, title, message, cooldown=0, show_cancel=True, parent=None):
        super().__init__(parent); self.setWindowTitle(dialog_type.capitalize()); self.setModal(True); self.setMinimumWidth(400)
        self.cooldown_seconds = cooldown
        main_layout = QVBoxLayout(self); main_layout.setSpacing(15)
        title_layout = QHBoxLayout(); icon_label = QLabel()
        
        style = self.style()
        if dialog_type == "warning": icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        elif dialog_type == "info": icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        else: icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        icon_label.setPixmap(icon.pixmap(32, 32))
        
        title_label = QLabel(title); title_label.setStyleSheet("font-size: 14pt; font-weight: 600; color: #FFFFFF;"); title_layout.addWidget(icon_label); title_layout.addWidget(title_label); title_layout.addStretch(); main_layout.addLayout(title_layout)
        message_label = QLabel(message); message_label.setWordWrap(True); main_layout.addWidget(message_label)
        button_layout = QHBoxLayout(); self.ok_button = QPushButton("OK"); self.ok_button.setObjectName("primary_button"); self.ok_button.clicked.connect(self.accept)
        if show_cancel:
            self.cancel_button = QPushButton("Cancel"); self.cancel_button.clicked.connect(self.reject); button_layout.addStretch(); button_layout.addWidget(self.cancel_button); button_layout.addWidget(self.ok_button)
        else:
            button_layout.addStretch(); button_layout.addWidget(self.ok_button)
        main_layout.addLayout(button_layout)
        if parent: self.setStyleSheet(parent.styleSheet())
        self.setStyleSheet(self.styleSheet() + "background-color: #2A2C3A;")
        if self.cooldown_seconds > 0: self.start_cooldown()

    def start_cooldown(self):
        self.ok_button.setEnabled(False); self.update_button_text(); self.timer = QTimer(self); self.timer.timeout.connect(self.update_cooldown); self.timer.start(1000)
    def update_cooldown(self):
        self.cooldown_seconds -= 1; self.update_button_text()
        if self.cooldown_seconds <= 0: self.timer.stop(); self.ok_button.setText("OK"); self.ok_button.setEnabled(True)
    def update_button_text(self): self.ok_button.setText(f"OK ({self.cooldown_seconds})")