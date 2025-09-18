from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QWidget
from PyQt6.QtCore import Qt, pyqtSignal

class GroupFrame(QFrame):
    """A styled frame with a title, used to group sections of the UI."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card_frame") # Use the main card style
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setObjectName("section_title")
        main_layout.addWidget(title_label)
        
        # We will add other widgets to this layout from the outside
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        main_layout.addLayout(self.content_layout)
        main_layout.addStretch() # Add stretch to push content up

class ValueSlider(QWidget):
    """A custom slider that includes a label to display its current value."""
    valueChanged = pyqtSignal(int)

    def __init__(self, min_val=0, max_val=100, initial_val=10, suffix="", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        
        self.value_label = QLabel()
        self.value_label.setMinimumWidth(50) # Ensure space for text
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.suffix = suffix
        
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)
        
        self.slider.valueChanged.connect(self._internal_value_changed)
        self.setValue(initial_val)

    def _internal_value_changed(self, value):
        self.value_label.setText(f"{value}{self.suffix}")
        self.valueChanged.emit(value)

    def value(self):
        return self.slider.value()

    def setValue(self, value):
        self.slider.setValue(value)
        self.value_label.setText(f"{value}{self.suffix}")
        
    def setRange(self, min_val, max_val):
        self.slider.setRange(min_val, max_val)
        
    def blockSignals(self, block):
        self.slider.blockSignals(block)