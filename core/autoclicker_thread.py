import time
import random
from PyQt6.QtCore import QThread, pyqtSignal
from pynput.mouse import Controller, Button

class AutoClickerThread(QThread):
    log_event = pyqtSignal(str)
    update_clicks = pyqtSignal(int)

    def __init__(self, state_manager):
        super().__init__()
        self.state_manager = state_manager
        self.mouse = Controller()
        self._running = False
        self.click_count = 0

    def run(self):
        self._running = True
        self.click_count = 0

        while self._running:
            settings = self.state_manager.get_settings()
            cps = settings['cps']

            self.mouse.click(Button[settings['mouse_button']], settings['click_type'])
            self.click_count += 1
            self.update_clicks.emit(self.click_count)

            if cps > 0:
                base_delay = 1.0 / cps
                delay = base_delay
                if settings['random_delay']:
                    random_offset = (random.random() - 0.5) * base_delay * 0.5
                    delay += random_offset

                if delay > 0:
                    time.sleep(delay)
            else:
                self.stop()

    def stop(self):
        self._running = False