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

    def start(self):
        if self.listener is None:
            self.listener_thread = QThread()
            self.moveToThread(self.listener_thread)
            self.listener_thread.started.connect(self._run_listener)
            self.listener_thread.start()

    def _run_listener(self):
        with keyboard.Listener(on_press=self.on_press) as self.listener:
            self.listener.join()

    def on_press(self, key):
        settings = self.state_manager.get_settings()
        start_hotkey_str = settings.get('start_hotkey', 'Key.f6')
        stop_hotkey_str = settings.get('stop_hotkey', 'Key.f7')

        try:
            key_str = ""
            if hasattr(key, 'name'):
                key_str = f"Key.{key.name}"
            elif hasattr(key, 'char'):
                key_str = key.char

            if key_str == start_hotkey_str:
                self.start_hotkey_triggered.emit()
            elif key_str == stop_hotkey_str:
                self.stop_hotkey_triggered.emit()
        except Exception as e:
            print(f"Error processing hotkey: {e}")

    def stop(self):
        if self.listener:
            self.listener.stop()
        if self.listener_thread:
            self.listener_thread.quit()
            self.listener_thread.wait()