from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame)
from PyQt6.QtCore import Qt, pyqtSignal

from ui.custom_widgets import ToggleSwitch, CustomComboBox
from ui.layout_widgets import GroupFrame, ValueSlider
from ui.views.warning_dialog import CustomDialog

def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

def create_setting_row(label_text, widget):
    row_layout = QHBoxLayout(); row_layout.setSpacing(10); label = QLabel(label_text); row_layout.addWidget(label, 1); row_layout.addWidget(widget); return row_layout

class GeneralView(QWidget):
    status_changed = pyqtSignal(str, str)
    def __init__(self, state_manager, db_manager, font_manager):
        super().__init__()
        self.state_manager = state_manager
        self.db_manager = db_manager
        self.font_manager = font_manager
        self.autoclicker_thread = None
        self.is_clicking = False
        
        # --- CPS MODES ARE RESTORED ---
        self.CPS_MODES = {
            "Normal": {"min": 1, "max": 30, "warning": None},
            "Fast": {"min": 31, "max": 50, "warning": "This speed may be suspicious in some applications."},
            "Extreme": {"min": 51, "max": 80, "warning": "This speed is highly detectable and increases the risk of being flagged or banned."},
            "Insane": {"min": 81, "max": 100, "warning": "Maximum output. This speed is virtually guaranteed to be detected. Use for experimental purposes only.", "cooldown": 10}
        }
        
        self.init_ui()
        self.state_manager.settings_updated.connect(self.update_ui_from_state)
        self.update_ui_from_state()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        # --- LEFT COLUMN: CONTROLS ---
        left_column = GroupFrame("Main")
        main_layout.addWidget(left_column, 1)
        
        self.start_button = QPushButton("Start Clicking")
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.start_autoclicker)
        self.stop_button = QPushButton("Stop Clicking")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_autoclicker)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        left_column.content_layout.addLayout(button_layout)
        
        self.mouse_button_combo = CustomComboBox(items=["Left", "Right", "Middle"])
        self.mouse_button_combo.currentTextChanged.connect(lambda val: self.state_manager.update_setting('mouse_button', val.lower()))
        left_column.content_layout.addLayout(create_setting_row("Mouse Button", self.mouse_button_combo))

        self.click_type_combo = CustomComboBox(items=["Single", "Double"])
        self.click_type_combo.currentTextChanged.connect(self.on_click_type_changed)
        left_column.content_layout.addLayout(create_setting_row("Click Type", self.click_type_combo))

        # --- RIGHT COLUMN: REFINEMENTS ---
        right_column = GroupFrame("Refinements")
        main_layout.addWidget(right_column, 1)

        # --- CPS MODE DROPDOWN IS RESTORED ---
        self.cps_mode_combo = CustomComboBox(items=list(self.CPS_MODES.keys()))
        self.cps_mode_combo.currentTextChanged.connect(self.on_cps_mode_changed)
        right_column.content_layout.addLayout(create_setting_row("CPS Mode", self.cps_mode_combo))
        
        self.cps_slider = ValueSlider(suffix=" CPS")
        self.cps_slider.valueChanged.connect(lambda v: self.state_manager.update_setting('cps', v))
        right_column.content_layout.addLayout(create_setting_row("Clicks Per Second", self.cps_slider))
        
        self.delay_toggle = ToggleSwitch()
        self.delay_toggle.toggled.connect(lambda checked: self.state_manager.update_setting('random_delay', checked))
        right_column.content_layout.addLayout(create_setting_row("Randomization", self.delay_toggle))
        
        apply_font_smoothing(self, self.font_manager.antialiased_font)

    def on_click_type_changed(self, text):
        click_type = 1 if text == "Single" else 2
        self.state_manager.update_setting('click_type', click_type)

    def on_cps_mode_changed(self, mode_text):
        mode_data = self.CPS_MODES.get(mode_text)
        if not mode_data: return

        previous_mode = self.state_manager.get_settings().get('cps_mode', 'Normal')
        if mode_data.get("warning"):
            dialog = CustomDialog("warning", f"{mode_text} Mode Selected", mode_data["warning"], cooldown=mode_data.get("cooldown", 0), parent=self)
            if not dialog.exec():
                self.cps_mode_combo.blockSignals(True)
                self.cps_mode_combo.setCurrentText(previous_mode)
                self.cps_mode_combo.blockSignals(False)
                return
        
        self.state_manager.update_setting('cps_mode', mode_text)

    def update_ui_from_state(self):
        settings = self.state_manager.get_settings()
        self.delay_toggle.blockSignals(True)
        self.mouse_button_combo.blockSignals(True)
        self.click_type_combo.blockSignals(True)
        self.cps_slider.blockSignals(True)
        self.cps_mode_combo.blockSignals(True)
        
        mode = settings.get('cps_mode', 'Normal')
        mode_data = self.CPS_MODES.get(mode, self.CPS_MODES['Normal'])
        min_cps, max_cps = mode_data['min'], mode_data['max']
        self.cps_slider.setRange(min_cps, max_cps)
        
        clamped_cps = max(min_cps, min(settings['cps'], max_cps))
        if clamped_cps != settings['cps']:
            self.state_manager.update_setting('cps', clamped_cps)
        else:
            self.cps_slider.setValue(clamped_cps)

        self.cps_mode_combo.setCurrentText(mode)
        
        self.delay_toggle.setChecked(settings['random_delay'])
        self.mouse_button_combo.setCurrentText(settings['mouse_button'].capitalize())
        click_type_text = "Single" if settings['click_type'] == 1 else "Double"
        self.click_type_combo.setCurrentText(click_type_text)

        self.delay_toggle.blockSignals(False)
        self.mouse_button_combo.blockSignals(False)
        self.click_type_combo.blockSignals(False)
        self.cps_slider.blockSignals(False)
        self.cps_mode_combo.blockSignals(False)

    def start_autoclicker(self):
        # ... (This logic is correct and does not need to change)
        from core.autoclicker_thread import AutoClickerThread
        if self.is_clicking: return
        self.is_clicking = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.autoclicker_thread = AutoClickerThread(self.state_manager)
        self.autoclicker_thread.start()
        
    def stop_autoclicker(self):
        # ... (This logic is correct and does not need to change)
        if not self.is_clicking: return
        self.is_clicking = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.autoclicker_thread and self.autoclicker_thread.isRunning():
            self.autoclicker_thread.stop()
            self.autoclicker_thread.wait()