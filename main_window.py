import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QListWidget, 
                             QStackedWidget, QListWidgetItem, QStatusBar, QLabel)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, QPropertyAnimation, QEasingCurve, QPoint, Qt

from core.icon_manager import IconManager
from database.database_manager import DatabaseManager
from core.state_manager import StateManager
from ui.views.general_view import GeneralView
from ui.views.targeting_view import TargetingView
from ui.views.profiles_view import ProfilesView
from ui.views.logs_view import LogsView
from ui.views.settings_view import SettingsView

def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

class UIManager:
    def __init__(self, stacked_widget):
        self.stacked_widget = stacked_widget
        self.current_index = -1
    def fade_to_index(self, index):
        if index == self.current_index: return
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'clearSelection'): current_widget.clearSelection()
        self.current_index = index
        if current_widget:
            self.fade_out_animation = QPropertyAnimation(current_widget, b"windowOpacity"); self.fade_out_animation.setDuration(120); self.fade_out_animation.setStartValue(1.0); self.fade_out_animation.setEndValue(0.0); self.fade_out_animation.finished.connect(lambda: self.switch_and_fade_in(index)); self.fade_out_animation.start()
        else: self.switch_and_fade_in(index)
    def switch_and_fade_in(self, index):
        self.stacked_widget.setCurrentIndex(index); new_widget = self.stacked_widget.currentWidget()
        if hasattr(new_widget, 'card_frame'):
            card = new_widget.card_frame; start_pos = QPoint(card.x(), card.y() + 20); end_pos = card.pos(); card.move(start_pos); self.slide_in = QPropertyAnimation(card, b"pos"); self.slide_in.setDuration(250); self.slide_in.setStartValue(start_pos); self.slide_in.setEndValue(end_pos); self.slide_in.setEasingCurve(QEasingCurve.Type.OutCubic); self.slide_in.start()
        new_widget.setWindowOpacity(0.0); self.fade_in_animation = QPropertyAnimation(new_widget, b"windowOpacity"); self.fade_in_animation.setDuration(200); self.fade_in_animation.setStartValue(0.0); self.fade_in_animation.setEndValue(1.0); self.fade_in_animation.start()

class MainWindow(QMainWindow):
    def __init__(self, font_manager):
        super().__init__()
        self.font_manager = font_manager
        self.setWindowTitle("Smite Autoclicker")
        self.setGeometry(100, 100, 1000, 720)
        self.setMinimumSize(850, 435)
        self.icons = IconManager()
        self.setWindowIcon(self.icons.get_icon("sidebar", "dashboard", "#FFFFFF", size=QSize(64, 64)))
        self.db_manager = DatabaseManager()
        self.state_manager = StateManager()
        self.init_ui()
        self.load_stylesheet("resources/styles/fluent_style.qss")
        self.init_status_bar()

    def init_ui(self):
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget); main_layout.setContentsMargins(10, 10, 10, 10); main_layout.setSpacing(10)
        
        # --- SIDEBAR IS RESTORED ---
        self.sidebar = QListWidget(); self.sidebar.setFixedWidth(220); self.sidebar.setIconSize(QSize(20, 20)); self.sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); main_layout.addWidget(self.sidebar)
        
        self.stacked_widget = QStackedWidget(); main_layout.addWidget(self.stacked_widget); self.ui_manager = UIManager(self.stacked_widget)
        
        self.general_view = GeneralView(self.state_manager, self.db_manager, self.font_manager)
        self.targeting_view = TargetingView(self.state_manager, self, self.font_manager)
        self.profiles_view = ProfilesView(self.state_manager, self.db_manager, self.font_manager)
        self.logs_view = LogsView(self.db_manager, self.font_manager)
        self.settings_view = SettingsView(self.state_manager, self.font_manager)
        
        self.stacked_widget.addWidget(self.general_view); self.stacked_widget.addWidget(self.targeting_view); self.stacked_widget.addWidget(self.profiles_view); self.stacked_widget.addWidget(self.logs_view); self.stacked_widget.addWidget(self.settings_view)
        
        self.add_sidebar_item("dashboard", "Dashboard", 0); self.add_sidebar_item("target", "Click Targeting", 1); self.add_sidebar_item("profile", "Profiles", 2); self.add_sidebar_item("logs", "Session Logs", 3); self.add_sidebar_item("settings", "Settings", 4)
        
        self.sidebar.currentRowChanged.connect(self.on_sidebar_selection_change); self.sidebar.setCurrentRow(0); self.ui_manager.current_index = 0; self.on_sidebar_selection_change(0)
        
        self.settings_view.hotkey_listener.start_hotkey_triggered.connect(self.general_view.start_autoclicker); self.settings_view.hotkey_listener.stop_hotkey_triggered.connect(self.general_view.stop_autoclicker)

    def on_sidebar_selection_change(self, index):
        self.ui_manager.fade_to_index(index)
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i); icon_name = item.data(Qt.ItemDataRole.UserRole)
            if i == index:
                item.setIcon(self.icons.get_icon("sidebar", icon_name, "#111111", size=QSize(20, 20)))
            else:
                item.setIcon(self.icons.get_icon("sidebar", icon_name, "#8A95C1", size=QSize(20, 20)))

    def init_status_bar(self):
        # The status bar is no longer part of this design
        pass

    def add_sidebar_item(self, icon_name, text, index):
        item = QListWidgetItem(self.icons.get_icon("sidebar", icon_name, "#8A95C1", size=QSize(20, 20)), text)
        item.setData(Qt.ItemDataRole.UserRole, icon_name); item.setSizeHint(QSize(200, 55)); self.sidebar.insertItem(index, item)
    
    def load_stylesheet(self, path):
        try:
            with open(path, "r") as f: self.setStyleSheet(f.read())
        except FileNotFoundError: print(f"Warning: Stylesheet not found at {path}")
    
    def closeEvent(self, event):
        if hasattr(self.general_view, 'autoclicker_thread') and self.general_view.autoclicker_thread:
            self.general_view.stop_autoclicker()
        self.settings_view.hotkey_listener.stop()
        event.accept()
