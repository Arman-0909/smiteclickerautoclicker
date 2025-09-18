from PyQt6.QtCore import QObject, pyqtSignal

class StateManager(QObject):
    settings_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._settings = {
            'cps': 10,
            'cps_mode': 'Normal', # <-- RE-ADDED
            'random_delay': False,
            'mouse_button': 'left',
            'click_type': 1,
            'target_mode': 'current_pos',
            'specific_pos_x': 100,
            'specific_pos_y': 100,
            'window_title': None,
            'start_hotkey': 'Key.f6',
            'stop_hotkey': 'Key.f7'
        }

    def get_settings(self):
        return self._settings.copy()

    def update_setting(self, key, value):
        if key in self._settings:
            self._settings[key] = value
            self.settings_updated.emit()
        else:
            raise KeyError(f"Setting '{key}' is not a valid setting.")

    def load_profile(self, profile_data):
        for key, value in profile_data.items():
            if key in self._settings:
                self._settings[key] = value
        self.settings_updated.emit()