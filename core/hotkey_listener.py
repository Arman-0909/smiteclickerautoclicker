from PyQt6.QtCore import QObject, pyqtSignal, QThread
from pynput import keyboard

class HotkeyListener(QObject):
    start_hotkey_triggered = pyqtSignal()
    stop_hotkey_triggered = pyqtSignal()

    def __init__(self, state_manager):
        super().__init__()
        self.state_manager = state_manager
        self.listener = None
        self.listener_thread = None
        # --- NEW: Internal state for Hold mode ---
        self.hold_mode_active = False

    def start(self):
        if self.listener is None:
            self.listener_thread = QThread()
            self.moveToThread(self.listener_thread)
            self.listener_thread.started.connect(self._run_listener)
            self.listener_thread.start()

    def _run_listener(self):
        # --- MODIFIED: Now listens for release events as well ---
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
            self.listener.join()

    def _key_to_str(self, key):
        """Helper method to convert a key event to a string."""
        if hasattr(key, 'name'):
            # This handles special keys like F6, Ctrl, etc.
            return f"Key.{key.name}"
        elif hasattr(key, 'char'):
            # This handles normal character keys
            return key.char
        return None

    def on_press(self, key):
        settings = self.state_manager.get_settings()
        hotkey_mode = settings.get('hotkey_mode', 'Toggle')
        start_hotkey_str = settings.get('start_hotkey', 'Key.f6')
        
        try:
            key_str = self._key_to_str(key)
            if not key_str: return

            if hotkey_mode == 'Toggle':
                stop_hotkey_str = settings.get('stop_hotkey', 'Key.f7')
                if key_str == start_hotkey_str:
                    self.start_hotkey_triggered.emit()
                elif key_str == stop_hotkey_str:
                    self.stop_hotkey_triggered.emit()
            
            elif hotkey_mode == 'Hold':
                # Start clicking only if it's the start key and not already active
                if key_str == start_hotkey_str and not self.hold_mode_active:
                    self.hold_mode_active = True
                    self.start_hotkey_triggered.emit()
        
        except Exception as e:
            print(f"Error processing hotkey press: {e}")

    def on_release(self, key):
        settings = self.state_manager.get_settings()
        hotkey_mode = settings.get('hotkey_mode', 'Toggle')
        start_hotkey_str = settings.get('start_hotkey', 'Key.f6')

        # Release events only matter in Hold mode
        if hotkey_mode != 'Hold':
            return
            
        try:
            key_str = self._key_to_str(key)
            if not key_str: return
            
            # Stop clicking if the start key is released and it was active
            if key_str == start_hotkey_str and self.hold_mode_active:
                self.hold_mode_active = False
                self.stop_hotkey_triggered.emit()

        except Exception as e:
            print(f"Error processing hotkey release: {e}")

    def stop(self):
        if self.listener:
            self.listener.stop()
        if self.listener_thread:
            self.listener_thread.quit()
            self.listener_thread.wait()