from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                             QPushButton, QLineEdit, QFrame, QListWidgetItem,
                             QListWidget)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from ui.views.warning_dialog import CustomDialog

# --- A dedicated widget for each item in the profile list ---
class ProfileItemWidget(QWidget):
    def __init__(self, profile_id, profile_name, parent=None):
        super().__init__(parent)
        self.profile_id = profile_id
        self.profile_name = profile_name
        
        self.init_ui()
        self.set_connections()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        
        self.name_label = QLabel(self.profile_name)
        font = self.name_label.font()
        font.setWeight(600)
        self.name_label.setFont(font)
        
        self.load_button = QPushButton("Load")
        self.load_button.setObjectName("primary_button")
        self.load_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_button.setFixedSize(80, 30)
        self.load_button.hide()

        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setFixedSize(80, 30)
        self.delete_button.hide()

        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.load_button)
        layout.addWidget(self.delete_button)

    def set_connections(self):
        # These signals will be connected in the main view
        pass

    def enterEvent(self, event):
        self.load_button.show()
        self.delete_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.load_button.hide()
        self.delete_button.hide()
        super().leaveEvent(event)

# --- Main Profiles View ---
class ProfilesView(QWidget):
    def __init__(self, state_manager, db_manager, font_manager):
        super().__init__()
        self.state_manager = state_manager
        self.db_manager = db_manager
        self.font_manager = font_manager
        self.init_ui()
        self.load_profiles_list()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.card_frame = QFrame(self)
        self.card_frame.setObjectName("card_frame")
        
        layout = QVBoxLayout(self.card_frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        title_label = QLabel("Manage Profiles")
        title_label.setObjectName("title_label")
        layout.addWidget(title_label)

        save_frame = QFrame()
        save_frame.setObjectName("setting_row")
        save_layout = QHBoxLayout(save_frame)
        self.profile_name_input = QLineEdit()
        self.profile_name_input.setPlaceholderText("Enter new profile name...")
        save_btn = QPushButton("Save Current Settings")
        save_btn.setObjectName("primary_button")
        save_btn.clicked.connect(self.save_current_profile)
        save_layout.addWidget(self.profile_name_input)
        save_layout.addWidget(save_btn)
        layout.addWidget(save_frame)

        self.profiles_list = QListWidget()
        self.profiles_list.setObjectName("profiles_list_widget")
        layout.addWidget(self.profiles_list, 1)
        
        main_layout.addWidget(self.card_frame)
        apply_font_smoothing(self, self.font_manager.antialiased_font)

    def clearSelection(self):
        self.profiles_list.clearSelection()

    def load_profiles_list(self):
        self.profiles_list.clear()
        profiles = self.db_manager.get_all_profiles()
        for profile_id, name in profiles:
            item = QListWidgetItem(self.profiles_list)
            item.setSizeHint(QSize(200, 50))
            
            profile_widget = ProfileItemWidget(profile_id, name)
            profile_widget.load_button.clicked.connect(lambda _, pid=profile_id: self.load_profile(pid))
            profile_widget.delete_button.clicked.connect(lambda _, pid=profile_id, pname=name: self.delete_profile(pid, pname))
            
            self.profiles_list.addItem(item)
            self.profiles_list.setItemWidget(item, profile_widget)
    
    def load_profile(self, profile_id):
        name, settings = self.db_manager.get_profile(profile_id)
        if settings:
            self.state_manager.load_profile(settings)
            dialog = CustomDialog("info", "Success", f"Profile '{name}' loaded successfully.", show_cancel=False, parent=self)
            dialog.exec()
    
    def delete_profile(self, profile_id, profile_name):
        dialog = CustomDialog("confirm", "Confirm Deletion", f"Are you sure you want to delete the profile '{profile_name}'?", parent=self)
        if dialog.exec():
            self.db_manager.delete_profile(profile_id)
            self.load_profiles_list()

    def save_current_profile(self):
        profile_name = self.profile_name_input.text().strip()
        if not profile_name:
            dialog = CustomDialog("warning", "Invalid Name", "Please enter a name for the profile.", show_cancel=False, parent=self)
            dialog.exec()
            return
        if self.db_manager.save_profile(profile_name, self.state_manager.get_settings()):
            self.load_profiles_list()
            self.profile_name_input.clear()
            dialog = CustomDialog("info", "Success", "Profile saved successfully.", show_cancel=False, parent=self)
            dialog.exec()
        else:
            dialog = CustomDialog("warning", "Error", "A profile with this name already exists.", show_cancel=False, parent=self)
            dialog.exec()

def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)
