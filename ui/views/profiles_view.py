from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                             QPushButton, QLineEdit, QFrame, QListWidgetItem,
                             QListWidget, QStyledItemDelegate, QStyle)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QEvent, QPoint, QRect
from PyQt6.QtGui import QColor, QBrush, QPainter
from ui.views.warning_dialog import CustomDialog
from core.icon_manager import IconManager

# --- START: DEFINITIVE, SELF-CONTAINED WIDGETS ---

class ProfileDelegate(QStyledItemDelegate):
    load_triggered = pyqtSignal(int)
    delete_triggered = pyqtSignal(int)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        profile_name = index.data(Qt.ItemDataRole.DisplayRole)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        text_color = QColor("#1A1B26") if option.state & QStyle.StateFlag.State_Selected else QColor("#A0A0A0")
        if option.state & QStyle.StateFlag.State_MouseOver:
            text_color = QColor("#F0F0F0")

        painter.setPen(text_color)
        font = painter.font()
        font.setWeight(600)
        painter.setFont(font)
        
        text_rect = option.rect.adjusted(12, 0, -180, 0) # Make space for buttons
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, profile_name)

    def sizeHint(self, option, index):
        return QSize(200, 50)

class ProfileListWidget(QListWidget):
    def __init__(self, delegate, parent=None):
        super().__init__(parent)
        self.setObjectName("profiles_list_widget")
        self.setMouseTracking(True)
        self.hover_index = -1
        self._delegate = delegate
        
        self.load_button = QPushButton("Load")
        self.load_button.setObjectName("primary_button")
        self.load_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_button.setFixedSize(80, 30)
        self.load_button.setParent(self.viewport())
        self.load_button.hide()

        self.delete_button = QPushButton("Delete")
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setFixedSize(80, 30)
        self.delete_button.setParent(self.viewport())
        self.delete_button.hide()
        
        self.load_button.clicked.connect(self._on_load_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)

    def _on_load_clicked(self):
        if self.hover_index != -1:
            self._delegate.load_triggered.emit(self.hover_index)
            
    def _on_delete_clicked(self):
        if self.hover_index != -1:
            self._delegate.delete_triggered.emit(self.hover_index)

    def updateButtons(self, index):
        if index.isValid() and self.model().rowCount() > 0:
            rect = self.visualRect(index)
            button_y = rect.y() + (rect.height() - self.load_button.height()) // 2
            
            self.delete_button.move(rect.right() - self.delete_button.width() - 10, button_y)
            self.load_button.move(self.delete_button.x() - self.load_button.width() - 5, button_y)
            
            self.load_button.show()
            self.delete_button.show()
        else:
            self.load_button.hide()
            self.delete_button.hide()

    def mouseMoveEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            if index.row() != self.hover_index:
                self.hover_index = index.row()
                self.updateButtons(index)
        super().mouseMoveEvent(event)
        
    def leaveEvent(self, event):
        self.hover_index = -1
        self.updateButtons(self.model().index(-1, -1)) # Invalid index
        super().leaveEvent(event)

# --- END: DEFINITIVE, SELF-CONTAINED WIDGETS ---

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

        self.profile_delegate = ProfileDelegate(self)
        self.profiles_list = ProfileListWidget(self.profile_delegate, self)
        self.profiles_list.setItemDelegate(self.profile_delegate)
        
        self.profile_delegate.load_triggered.connect(self.load_profile_by_row)
        self.profile_delegate.delete_triggered.connect(self.delete_profile_by_row)

        layout.addWidget(self.profiles_list, 1)
        
        main_layout.addWidget(self.card_frame)

        apply_font_smoothing(self, self.font_manager.antialiased_font)

    def clearSelection(self):
        self.profiles_list.clearSelection()

    def load_profiles_list(self):
        self.profiles_list.clear()
        for profile_id, name in self.db_manager.get_all_profiles():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, profile_id)
            self.profiles_list.addItem(item)
    
    def load_profile_by_row(self, row):
        item = self.profiles_list.item(row)
        if not item: return
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        name, settings = self.db_manager.get_profile(profile_id)
        if settings:
            self.state_manager.load_profile(settings)
            dialog = CustomDialog("info", "Success", f"Profile '{name}' loaded successfully.", show_cancel=False, parent=self)
            dialog.exec()
    
    def delete_profile_by_row(self, row):
        item = self.profiles_list.item(row)
        if not item: return
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        profile_name = item.text()
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