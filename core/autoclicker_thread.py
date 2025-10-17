import time
import random
from PyQt6.QtCore import QThread, pyqtSignal
from pynput.mouse import Controller, Button
import pygetwindow as gw

class AutoClickerThread(QThread):
    log_event = pyqtSignal(str)
    update_clicks = pyqtSignal(int)
    # --- NEW SIGNAL ---
    autoclicker_stopped = pyqtSignal()

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

            target_window = None
            if settings['window_targeting_enabled']:
                window_title = settings.get('target_window')
                if window_title:
                    windows = gw.getWindowsWithTitle(window_title)
                    if windows:
                        target_window = windows[0]
                    else:
                        time.sleep(0.1)
                        continue
                else:
                    time.sleep(0.1)
                    continue

            click_pos = None
            if settings['target_mode'] == 'specific_pos':
                click_pos = (settings['specific_pos_x'], settings['specific_pos_y'])
            else:
                click_pos = self.mouse.position

            can_click = True
            if target_window:
                win_box = target_window.box
                is_inside = (win_box.left <= click_pos[0] < win_box.left + win_box.width and
                             win_box.top <= click_pos[1] < win_box.top + win_box.height)
                if not is_inside:
                    can_click = False

            if can_click:
                if settings['target_mode'] == 'specific_pos':
                    self.mouse.position = click_pos

                self.mouse.click(Button[settings['mouse_button']], settings['click_type'])
                self.click_count += 1
                self.update_clicks.emit(self.click_count)

                # --- NEW LOGIC FOR CLICK LIMIT ---
                if settings['click_limit_enabled']:
                    if self.click_count >= settings['click_limit_count']:
                        self.stop()
                        # Use break to exit the loop immediately
                        break

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
        
        # --- EMIT NEW SIGNAL ---
        # This will run when the loop finishes for any reason (stopped or limit reached)
        self.autoclicker_stopped.emit()

    def stop(self):
        self._running = False