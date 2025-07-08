from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, 
    QPushButton, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QPropertyAnimation, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush

class ClickableLabel(QLabel):
    clicked = Signal()
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class HistoryWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alert History")
        self.setMinimumSize(600, 400)
        
        # Gradient background (matching dashboard)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectMode)
        gradient.setColorAt(0, QColor("#1e3c72"))
        gradient.setColorAt(1, QColor("#2a5298"))
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        central_widget.setAutoFillBackground(True)
        central_widget.setPalette(palette)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Content frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        
        # Title
        title = QLabel("Alert History Summary")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e3c72; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title)
        
        # Statistics summary
        total_alerts = 38  # This would come from your data
        sensor_count = 5   # This would come from your data
        summary = QLabel(f"Total Alerts: {total_alerts} | Active Sensors: {sensor_count}")
        summary.setFont(QFont("Arial", 11))
        summary.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(summary)
        
        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Sensor Type", "ID", "Location", "Alert Count"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Sample data - replace with your actual data
        self.alert_data = [
            {"type": "Motion Sensor", "id": "MS-001", "location": "Main Entrance", "alerts": 12},
            {"type": "Door Sensor", "id": "DS-005", "location": "Back Door", "alerts": 8},
            {"type": "Glass Break", "id": "GB-003", "location": "Living Room", "alerts": 3},
            {"type": "Motion Sensor", "id": "MS-007", "location": "Garage", "alerts": 15},
            {"type": "Temperature", "id": "TEMP-009", "location": "Server Room", "alerts": 0}
        ]
        
        # Populate table
        self.table.setRowCount(len(self.alert_data))
        for row, data in enumerate(self.alert_data):
            self.table.setItem(row, 0, QTableWidgetItem(data["type"]))
            self.table.setItem(row, 1, QTableWidgetItem(data["id"]))
            self.table.setItem(row, 2, QTableWidgetItem(data["location"]))
            
            # Color code alert counts
            alert_item = QTableWidgetItem(str(data["alerts"]))
            if data["alerts"] > 10:
                alert_item.setForeground(QColor("#c0392b"))  # Red for high alerts
            elif data["alerts"] > 5:
                alert_item.setForeground(QColor("#e67e22"))  # Orange for medium
            else:
                alert_item.setForeground(QColor("#27ae60"))  # Green for low
                
            self.table.setItem(row, 3, alert_item)
        
        frame_layout.addWidget(self.table)
        
        # Close button
        btn_close = QPushButton("Close")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 25px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_close.clicked.connect(self.close)
        frame_layout.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(frame)
        
        # Fade-in animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Dashboard")
        self.setMinimumSize(500, 350)

        # Gradient background
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectMode)
        gradient.setColorAt(0, QColor("#1e3c72"))
        gradient.setColorAt(1, QColor("#2a5298"))
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        central_widget.setAutoFillBackground(True)
        central_widget.setPalette(palette)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Styled frame
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)

        # Title
        title = QLabel("Security Controls")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e3c72;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title)

        # Status Switch
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)
        
        status_label = QLabel("Status of the sensor:")
        status_label.setStyleSheet("""
            color: #555555;
            font-size: 14px;
            font-weight: bold;
        """)
        status_layout.addWidget(status_label)

        self.toggle_status = QPushButton("OFF")
        self.toggle_status.setCheckable(True)
        self.toggle_status.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
                max-width: 80px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
        """)
        self.toggle_status.toggled.connect(self.update_toggle_text)
        status_layout.addWidget(self.toggle_status)
        status_layout.addStretch()
        frame_layout.addWidget(status_container)

        # Alert Level Slider
        slider_container = QWidget()
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setSpacing(5)
        
        slider_title = QLabel("Set the level of the alarm")
        slider_title.setStyleSheet("""
            color: #555555;
            font-size: 14px;
            font-weight: bold;
        """)
        slider_layout.addWidget(slider_title)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 2)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        
        # Base slider style
        self.slider.setStyleSheet("""
            QSlider {
                min-height: 30px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #d3d3d3;
                border-radius: 4px;
                margin: 0 10px;
            }
            QSlider::handle:horizontal {
                width: 20px;
                height: 20px;
                margin: -6px -10px;
                background: #1e3c72;
                border-radius: 10px;
            }
        """)
        
        self.slider.valueChanged.connect(self.update_slider_style)
        slider_layout.addWidget(self.slider)

        # Level labels
        self.labels_container = QWidget()
        labels_layout = QHBoxLayout(self.labels_container)
        labels_layout.setContentsMargins(10, 0, 10, 0)
        
        self.level_labels = []
        for i, text in enumerate(["Low", "Medium", "High"]):
            label = ClickableLabel(text)
            label.setProperty('level', i)
            label.setStyleSheet("""
                ClickableLabel {
                    color: #555555;
                    padding: 0 15px;
                }
                ClickableLabel:hover {
                    color: #333333;
                    font-weight: bold;
                }
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.clicked.connect(self.on_label_clicked)
            labels_layout.addWidget(label)
            self.level_labels.append(label)
        
        slider_layout.addWidget(self.labels_container)
        frame_layout.addWidget(slider_container)

        # Initialize
        self.update_slider_style(0)

        # History button
        self.button_history = QPushButton("Show Alert History")
        self.button_history.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.button_history.clicked.connect(self.show_history)
        frame_layout.addWidget(self.button_history, 0, Qt.AlignmentFlag.AlignCenter)

        # Logout button
        self.button_logout = QPushButton("Logout")
        self.button_logout.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        frame_layout.addWidget(self.button_logout, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(frame)

        # Fade-in animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def update_toggle_text(self, checked):
        self.toggle_status.setText("ON" if checked else "OFF")

    def on_label_clicked(self):
        """Handle label clicks without lambda issues"""
        sender = self.sender()
        level = sender.property('level')
        self.slider.setValue(level)

    def update_slider_style(self, value):
        """Update slider and label styles based on current value"""
        # Color mapping
        colors = {
            0: ("#4CAF50", "#388E3C"),  # Green (Low)
            1: ("#2196F3", "#1976D2"),  # Blue (Medium)
            2: ("#FF9800", "#F57C00")   # Orange (High)
        }
        
        # Update slider style
        color, dark_color = colors[value]
        self.slider.setStyleSheet(f"""
            QSlider {{
                min-height: 30px;
            }}
            QSlider::groove:horizontal {{
                height: 8px;
                background: #d3d3d3;
                border-radius: 4px;
                margin: 0 10px;
            }}
            QSlider::sub-page:horizontal {{
                background: {color};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                width: 20px;
                height: 20px;
                margin: -6px -10px;
                background: {dark_color};
                border-radius: 10px;
            }}
        """)
        
        # Update label styles
        for i, label in enumerate(self.level_labels):
            if i == value:
                label.setStyleSheet(f"""
                    ClickableLabel {{
                        color: {dark_color};
                        font-weight: bold;
                        padding: 0 15px;
                    }}
                """)
            else:
                label.setStyleSheet("""
                    ClickableLabel {
                        color: #555555;
                        padding: 0 15px;
                    }
                    ClickableLabel:hover {
                        color: #333333;
                        font-weight: bold;
                    }
                """)
    
    def show_history(self):
        """Show the alert history window"""
        self.history_window = HistoryWindow(self)
        self.history_window.show()
        