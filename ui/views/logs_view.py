from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, 
                             QHeaderView, QFrame, QStyledItemDelegate, QStyle)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QEvent, QPoint, QRect
from PyQt6.QtGui import QColor, QBrush, QPainter
from ui.views.warning_dialog import CustomDialog
from core.icon_manager import IconManager

# New helper function
def apply_font_smoothing(widget, font):
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

class LogsTableWidget(QTableWidget):
    # ... (unchanged)
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

class DeleteDelegate(QStyledItemDelegate):
    # ... (unchanged)
    delete_triggered = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent); self.icons = IconManager()
    def paint(self, painter, option, index):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing); super().paint(painter, option, index); is_hovered = option.state & QStyle.StateFlag.State_MouseOver; icon = self.icons.get_icon("session-logs", "delete", "#8A95C1"); hover_icon = self.icons.get_icon("session-logs", "delete", "#FFFFFF"); pixmap = icon.pixmap(QSize(14, 14));
        if is_hovered:
            pixmap = hover_icon.pixmap(QSize(14, 14)); hover_rect = QRect(option.rect.center().x() - 15, option.rect.center().y() - 15, 30, 30); painter.setBrush(QBrush(QColor("#7A2A2A"))); painter.setPen(Qt.PenStyle.NoPen); painter.drawRoundedRect(hover_rect, 5, 5)
        x = option.rect.x() + (option.rect.width() - pixmap.width()) // 2; y = option.rect.y() + (option.rect.height() - pixmap.height()) // 2; painter.drawPixmap(QPoint(x, y), pixmap)
    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            if option.rect.contains(event.pos()): self.delete_triggered.emit(index.row()); return True
        return super().editorEvent(event, model, option, index)
    def sizeHint(self, option, index): return QSize(70, 40)

class LogsView(QWidget):
    # --- THE FIX: Accept font_manager ---
    def __init__(self, db_manager, font_manager):
        super().__init__()
        self.db_manager = db_manager
        self.font_manager = font_manager # <-- Store font_manager
        self.icons = IconManager()
        self.init_ui()
        self.load_logs()

    def init_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0); self.card_frame = QFrame(self); self.card_frame.setObjectName("card_frame"); layout = QVBoxLayout(self.card_frame); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15); title_label = QLabel("Session Logs"); title_label.setObjectName("title_label"); layout.addWidget(title_label)
        self.log_table = LogsTableWidget(); self.log_table.setColumnCount(5); self.log_table.setHorizontalHeaderLabels(["Start Time", "End Time", "Duration (s)", "Total Clicks", "Actions"]); self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.log_table.setAlternatingRowColors(True); self.log_table.setShowGrid(False); self.log_table.verticalHeader().setVisible(False)
        header = self.log_table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch); header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed); header.setStretchLastSection(False); self.log_table.setColumnWidth(4, 70)
        self.delete_delegate = DeleteDelegate(self.log_table); self.log_table.setItemDelegateForColumn(4, self.delete_delegate); self.delete_delegate.delete_triggered.connect(self.delete_log_entry_by_row)
        layout.addWidget(self.log_table)
        btn_layout = QHBoxLayout(); refresh_btn = QPushButton("Refresh"); refresh_btn.setObjectName("primary_button"); refresh_btn.setIcon(self.icons.get_icon("session-logs", "refresh", "#111111")); refresh_btn.clicked.connect(self.load_logs); clear_btn = QPushButton("Clear All Logs"); clear_btn.setIcon(self.icons.get_icon("session-logs", "clearall", "#8A95C1")); clear_btn.clicked.connect(self.clear_logs); btn_layout.addStretch(); btn_layout.addWidget(refresh_btn); btn_layout.addWidget(clear_btn); layout.addLayout(btn_layout)
        main_layout.addWidget(self.card_frame)
        
        # --- THE FIX: Apply font smoothing ---
        apply_font_smoothing(self, self.font_manager.antialiased_font)

    # ... (rest of logs_view.py is unchanged)
    def clearSelection(self): self.log_table.clearSelection()
    def load_logs(self):
        self.log_table.setRowCount(0)
        try:
            logs = self.db_manager.get_all_logs()
            self.log_table.setRowCount(len(logs))
            for row_idx, row_data in enumerate(logs):
                log_id, start, end, duration, clicks = row_data
                item_start = QTableWidgetItem(start); item_start.setData(Qt.ItemDataRole.UserRole, log_id); self.log_table.setItem(row_idx, 0, item_start); self.log_table.setItem(row_idx, 1, QTableWidgetItem(end)); self.log_table.setItem(row_idx, 2, QTableWidgetItem(f"{duration:.2f}")); self.log_table.setItem(row_idx, 3, QTableWidgetItem(str(clicks)))
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