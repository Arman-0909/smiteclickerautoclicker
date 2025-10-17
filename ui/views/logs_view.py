from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, 
                             QHeaderView, QFrame, QStyledItemDelegate, QStyle)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QEvent, QPoint, QRect
from PyQt6.QtGui import QColor, QBrush, QPainter, QPen
from ui.views.warning_dialog import CustomDialog
from core.icon_manager import IconManager
from ..layout_widgets import GroupFrame

def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

class LogsTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setMouseTracking(True); self.hover_row = -1
    def mouseMoveEvent(self, event):
        index = self.indexAt(event.pos()); current_row = index.row() if index.isValid() else -1
        if current_row != self.hover_row:
            if self.hover_row != -1: update_rect = QRect(0, self.rowViewportPosition(self.hover_row), self.viewport().width(), self.rowHeight(self.hover_row)); self.viewport().update(update_rect)
            if current_row != -1: update_rect = QRect(0, self.rowViewportPosition(current_row), self.viewport().width(), self.rowHeight(current_row)); self.viewport().update(update_rect)
            self.hover_row = current_row
        super().mouseMoveEvent(event)
    def leaveEvent(self, event):
        if self.hover_row != -1: update_rect = QRect(0, self.rowViewportPosition(self.hover_row), self.viewport().width(), self.rowHeight(self.hover_row)); self.viewport().update(update_rect)
        self.hover_row = -1; super().leaveEvent(event)

# --- START: DEFINITIVE, PIXEL-PERFECT DELEGATE ---
class DeleteDelegate(QStyledItemDelegate):
    delete_triggered = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icons = IconManager()

    def paint(self, painter, option, index):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        # --- Draw Background ---
        if is_selected:
            painter.fillRect(option.rect, QColor("#8A95C1"))
        elif index.row() % 2 == 1: # Alternate row color
             painter.fillRect(option.rect, QColor("#111111"))
        else:
             painter.fillRect(option.rect, QColor("#151515"))
        
        # --- Draw Icon ---
        icon_color = "#111111" if is_selected else "#8A95C1"
        icon = self.icons.get_icon("session-logs", "delete", icon_color)
        
        pixmap = icon.pixmap(QSize(14, 14))
        
        # --- Draw Hover Effect ---
        if is_hovered:
            # CORRECTED Centering
            hover_rect_size = 28
            x = option.rect.x() + (option.rect.width() - hover_rect_size) // 2
            y = option.rect.y() + (option.rect.height() - hover_rect_size) // 2
            hover_rect = QRect(x, y, hover_rect_size, hover_rect_size)

            painter.setBrush(QBrush(QColor("#454545")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(hover_rect, 5, 5)
            
            # Use a white icon on hover
            hover_icon = self.icons.get_icon("session-logs", "delete", "#FFFFFF")
            pixmap = hover_icon.pixmap(QSize(14, 14))

        # Center the pixmap inside the cell
        px = option.rect.x() + (option.rect.width() - pixmap.width()) // 2
        py = option.rect.y() + (option.rect.height() - pixmap.height()) // 2
        painter.drawPixmap(QPoint(px, py), pixmap)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            if option.rect.contains(event.pos()): self.delete_triggered.emit(index.row()); return True
        return super().editorEvent(event, model, option, index)
    def sizeHint(self, option, index): return QSize(70, 40)
# --- END: DEFINITIVE, PIXEL-PERFECT DELEGATE ---

class LogsView(QWidget):
    def __init__(self, db_manager, font_manager):
        super().__init__(); self.db_manager = db_manager; self.font_manager = font_manager; self.icons = IconManager(); self.init_ui(); self.load_logs()

    def init_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0); self.card_frame = GroupFrame("Session Logs"); main_layout.addWidget(self.card_frame)
        self.log_table = LogsTableWidget(); self.log_table.setColumnCount(5); self.log_table.setHorizontalHeaderLabels(["Start Time", "End Time", "Duration (s)", "Total Clicks", "Actions"]); self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.log_table.setAlternatingRowColors(False); self.log_table.setShowGrid(False); self.log_table.verticalHeader().setVisible(False)
        header = self.log_table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch); header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed); header.setStretchLastSection(False); self.log_table.setColumnWidth(4, 70)
        
        # --- DELEGATE SETUP IS UNCHANGED ---
        self.delete_delegate = DeleteDelegate(self.log_table)
        self.log_table.setItemDelegateForColumn(4, self.delete_delegate)
        self.delete_delegate.delete_triggered.connect(self.delete_log_entry_by_row)
        
        self.card_frame.content_layout.addWidget(self.log_table)
        
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh"); refresh_btn.setObjectName("primary_button");
        clear_btn = QPushButton("Clear All Logs")
        refresh_btn.clicked.connect(self.load_logs)
        clear_btn.clicked.connect(self.clear_logs)
        btn_layout.addStretch(); btn_layout.addWidget(refresh_btn); btn_layout.addWidget(clear_btn)
        self.card_frame.content_layout.addLayout(btn_layout)
        
        apply_font_smoothing(self, self.font_manager.antialiased_font)

    def clearSelection(self): self.log_table.clearSelection()
    def load_logs(self):
        self.log_table.setRowCount(0)
        try:
            logs = self.db_manager.get_all_logs()
            self.log_table.setRowCount(len(logs))
            for row_idx, row_data in enumerate(logs):
                log_id, start, end, duration, clicks = row_data
                item_start = QTableWidgetItem(start); item_start.setData(Qt.ItemDataRole.UserRole, log_id); self.log_table.setItem(row_idx, 0, item_start)
                item_end = QTableWidgetItem(end); self.log_table.setItem(row_idx, 1, item_end)
                item_duration = QTableWidgetItem(f"{duration:.2f}"); self.log_table.setItem(row_idx, 2, item_duration)
                item_clicks = QTableWidgetItem(str(clicks)); self.log_table.setItem(row_idx, 3, item_clicks)
                # We also need to set an item in the delegate column for it to exist
                self.log_table.setItem(row_idx, 4, QTableWidgetItem())
                
                # --- APPLY THEME COLOR TO TEXT ---
                for col in range(4):
                    item = self.log_table.item(row_idx, col)
                    item.setForeground(QColor("#8A95C1"))

        except Exception as e: dialog = CustomDialog("warning", "Database Error", f"Could not load logs.\nError: {e}", show_cancel=False, parent=self); dialog.exec()
    
    def delete_log_entry_by_row(self, row):
        item = self.log_table.item(row, 0);
        if not item: return
        log_id = item.data(Qt.ItemDataRole.UserRole)
        dialog = CustomDialog("confirm", "Confirm Deletion", "Are you sure you want to delete this specific log entry?", parent=self)
        if dialog.exec():
            try: self.db_manager.delete_log(log_id); self.load_logs()
            except Exception as e: error_dialog = CustomDialog("warning", "Database Error", f"Could not delete the log entry.\nError: {e}", show_cancel=False, parent=self); error_dialog.exec()
    
    def clear_logs(self):
        dialog = CustomDialog("confirm", "Confirm Clear", "Are you sure you want to delete all session logs? This action cannot be undone.", parent=self)
        if dialog.exec():
            try: self.db_manager.clear_logs(); self.load_logs()
            except Exception as e: error_dialog = CustomDialog("warning", "Database Error", f"Could not clear logs.\nError: {e}", show_cancel=False, parent=self); error_dialog.exec()
