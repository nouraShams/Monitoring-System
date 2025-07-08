from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, 
    QPushButton, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush
from database import MonitoringDB  # Import the database class
from PySide6.QtCore import QTimer
 
import socket
import struct
from enum import IntEnum

# Define Modbus constants
MODBUS_PORT = 502
MODBUS_UNIT_ID = 1
class SensorState(IntEnum):
    OPEN = 0
    CLOSED = 1
    UNKNOWN = 2
    LOW_BATTERY = 3

class ModbusFunction(IntEnum):
    READ_COILS = 1
    READ_DISCRETE_INPUTS = 2
    WRITE_SINGLE_COIL = 5


class ClickableLabel(QLabel):
    clicked = Signal()
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class HistoryWindow(QMainWindow):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Alert History")
        self.setMinimumSize(600, 400)
        
        # Database connection
        self.db = MonitoringDB()
        
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
        
        # Get alert summary data from database
        summary_data = self.db.get_alert_summary()
        
        # Statistics summary
        total_alerts = sum(item['alert_count'] for item in summary_data)
        sensor_count = len(summary_data)
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
        
        # Populate table with real data
        self.table.setRowCount(len(summary_data))
        for row, data in enumerate(summary_data):
            self.table.setItem(row, 0, QTableWidgetItem(data["sensor_type"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(data["sensor_id"])))  # Convert ID to string
            self.table.setItem(row, 2, QTableWidgetItem(data["location"]))
            
            # Color code alert counts
            alert_item = QTableWidgetItem(str(data["alert_count"]))
            if data["alert_count"] > 10:
                alert_item.setForeground(QColor("#c0392b"))  # Red for high alerts
            elif data["alert_count"] > 5:
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
    
    def closeEvent(self, event):
        # Close database connection
        self.db.close()
        event.accept()
MODBUS_PORT = 502
MODBUS_UNIT_ID = 1
class DashboardWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Security Dashboard")
        self.setMinimumSize(500, 350)
        
        # Initialize connection parameters
        self.modbus_ip = "192.168.1.100"  # Default IP for receiver
        self.modbus_connected = False
        
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
        
        # Connection status UI
        connection_container = QWidget()
        connection_layout = QHBoxLayout(connection_container)
        connection_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_connect = QPushButton("Connect to Receiver")
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.btn_connect.clicked.connect(self.toggle_connection)
        
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        connection_layout.addWidget(self.btn_connect)
        connection_layout.addWidget(self.connection_status)
        frame_layout.addWidget(connection_container)
        
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

        # ADD HISTORY BUTTON HERE
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

        # Sensor state display
        self.sensor_state = QLabel("State: UNKNOWN")
        self.sensor_state.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        frame_layout.addWidget(self.sensor_state)

        # ADD LOGOUT BUTTON
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
        self.button_logout.clicked.connect(self.logout)
        frame_layout.addWidget(self.button_logout, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(frame)

        # Initialize polling timer
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.poll_sensor_state)
        self.poll_timer.setInterval(5000)  # 5 seconds

        # Fade-in animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    # ADD MISSING METHODS
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
        self.history_window = HistoryWindow(self, self.user)
        self.history_window.show()
    
    def logout(self):
        """Handle logout"""
        self.close()
    
    # Connection management methods
    def toggle_connection(self):
        """Toggle connection to the MODBUS receiver"""
        if not self.modbus_connected:
            self.connect_to_modbus()
        else:
            self.disconnect_from_modbus()

    def connect_to_modbus(self):
        """Establish connection to MODBUS receiver"""
        try:
            self.modbus_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.modbus_socket.settimeout(2.0)
            self.modbus_socket.connect((self.modbus_ip, MODBUS_PORT))
            self.modbus_connected = True
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.btn_connect.setText("Disconnect")
            self.poll_timer.start()
            
            # Initialize sensor configuration
            self.configure_sensor()
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", 
                               f"Could not connect to receiver:\n{str(e)}")

    def disconnect_from_modbus(self):
        """Close connection to MODBUS receiver"""
        self.poll_timer.stop()
        if hasattr(self, 'modbus_socket') and self.modbus_connected:
            self.modbus_socket.close()
        self.modbus_connected = False
        self.connection_status.setText("Disconnected")
        self.connection_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.btn_connect.setText("Connect to Receiver")
        self.sensor_state.setText("State: DISCONNECTED")
        self.sensor_state.setStyleSheet("font-weight: bold; color: #e74c3c;")

    def poll_sensor_state(self):
        """Poll the sensor for current state"""
        if not self.modbus_connected:
            return
        
        try:
            # Read discrete inputs (function code 2)
            request = self.create_modbus_request(
                function=ModbusFunction.READ_DISCRETE_INPUTS,
                address=0,
                count=1
            )
            self.modbus_socket.send(request)
            response = self.modbus_socket.recv(256)
            
            if len(response) < 5:
                raise ValueError("Invalid response length")
            
            state_byte = response[8]
            state = SensorState.OPEN if (state_byte & 0x01) == 0 else SensorState.CLOSED
            self.update_sensor_state_ui(state)
            
        except Exception as e:
            print(f"Polling error: {str(e)}")
            self.sensor_state.setText("State: ERROR")
            self.sensor_state.setStyleSheet("font-weight: bold; color: #e74c3c;")

    def create_modbus_request(self, function, address, count=0, value=0):
        """Create MODBUS TCP request"""
        transaction_id = 0x0001
        protocol_id = 0x0000
        unit_id = MODBUS_UNIT_ID
        
        if function in [ModbusFunction.READ_COILS, ModbusFunction.READ_DISCRETE_INPUTS]:
            length = 6
            data = struct.pack(">HHH", function, address, count)
        elif function == ModbusFunction.WRITE_SINGLE_COIL:
            length = 6
            data = struct.pack(">HHH", function, address, value)
        else:
            raise ValueError("Unsupported function code")
        
        header = struct.pack(">HHH", transaction_id, protocol_id, length)
        return header + struct.pack("B", unit_id) + data

    def configure_sensor(self):
        """Configure sensor transmission parameters"""
        try:
            config_request = self.create_modbus_request(
                function=ModbusFunction.WRITE_SINGLE_COIL,
                address=0x100,  # Example configuration address
                value=0x01       # State change + periodic mode
            )
            self.modbus_socket.send(config_request)
            response = self.modbus_socket.recv(256)
            
        except Exception as e:
            print(f"Configuration error: {str(e)}")

    def update_sensor_state_ui(self, state):
        """Update UI based on sensor state"""
        if state == SensorState.OPEN:
            self.sensor_state.setText("State: OPEN")
            self.sensor_state.setStyleSheet("font-weight: bold; color: #e74c3c;")
        elif state == SensorState.CLOSED:
            self.sensor_state.setText("State: CLOSED")
            self.sensor_state.setStyleSheet("font-weight: bold; color: #27ae60;")
        else:
            self.sensor_state.setText("State: UNKNOWN")
            self.sensor_state.setStyleSheet("font-weight: bold; color: #7f8c8d;")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Disconnect from MODBUS receiver
        if hasattr(self, 'modbus_connected') and self.modbus_connected:
            self.disconnect_from_modbus()
        
        # Close database connection
        if hasattr(self, 'db'):
            self.db.close()
        
        event.accept()
def poll_sensor_state(self):
    if not self.modbus_connected:
        return
    
    try:
        # Read discrete inputs (function code 2)
        # Assuming contact sensor is at address 0
        request = self.create_modbus_request(
            function=ModbusFunction.READ_DISCRETE_INPUTS,
            address=0,
            count=1
        )
        self.modbus_socket.send(request)
        response = self.modbus_socket.recv(256)
        
        # Parse response
        if len(response) < 5:
            raise ValueError("Invalid response length")
        
        # Byte 8 contains the state (bit 0)
        state_byte = response[8]
        state = SensorState.OPEN if (state_byte & 0x01) == 0 else SensorState.CLOSED
        
        # Update UI
        self.update_sensor_state_ui(state)
        
        # Check battery every 10 polls (every 50 seconds)
        if self.poll_timer.interval() * 10 > 50000:
            self.check_battery_status()
        
    except Exception as e:
        print(f"Polling error: {str(e)}")
        self.sensor_state.setText("State: ERROR")
        self.sensor_state.setStyleSheet("font-weight: bold; color: #e74c3c;")

def configure_sensor(self):
    """Configure sensor transmission parameters"""
    try:
        # Set to send on state change + periodic every 5 minutes (as per specs)
        # (This would require knowing the specific configuration registers)
        config_request = self.create_modbus_request(
            function=ModbusFunction.WRITE_SINGLE_COIL,
            address=0x100,  # Example configuration address
            value=0x01       # State change + periodic mode
        )
        self.modbus_socket.send(config_request)
        response = self.modbus_socket.recv(256)
        
    except Exception as e:
        print(f"Configuration error: {str(e)}")

def create_modbus_request(self, function, address, count=0, value=0):
    """Create MODBUS TCP request"""
    transaction_id = 0x0001  # Can increment for each request
    protocol_id = 0x0000
    unit_id = MODBUS_UNIT_ID
    
    if function in [ModbusFunction.READ_COILS, ModbusFunction.READ_DISCRETE_INPUTS]:
        # Read request
        length = 6
        data = struct.pack(">HHH", function, address, count)
    elif function == ModbusFunction.WRITE_SINGLE_COIL:
        # Write request
        length = 6
        data = struct.pack(">HHH", function, address, value)
    else:
        raise ValueError("Unsupported function code")
    
    header = struct.pack(">HHH", transaction_id, protocol_id, length)
    return header + struct.pack("B", unit_id) + data

def update_sensor_state_ui(self, state):
    if state == SensorState.OPEN:
        self.sensor_state.setText("State: OPEN")
        self.sensor_state.setStyleSheet("font-weight: bold; color: #e74c3c;")  # Red for alarm
    elif state == SensorState.CLOSED:
        self.sensor_state.setText("State: CLOSED")
        self.sensor_state.setStyleSheet("font-weight: bold; color: #27ae60;")  # Green for normal
    else:
        self.sensor_state.setText("State: UNKNOWN")
        self.sensor_state.setStyleSheet("font-weight: bold; color: #7f8c8d;")

def update_battery_ui(self, level):
    color = "#27ae60"  # Green
    if level < 20:
        color = "#e74c3c"  # Red
    elif level < 40:
        color = "#f39c12"  # Orange
    
    self.battery_indicator.setStyleSheet(f"""
        background-color: {color};
        border: 1px solid #7f8c8d;
        border-radius: 3px;
    """)
    self.battery_indicator.setToolTip(f"Battery: {level}%")

def check_battery_status(self):
    try:
        # Read battery status register (example address)
        request = self.create_modbus_request(
            function=ModbusFunction.READ_DISCRETE_INPUTS,
            address=0x200,  # Battery status register
            count=1
        )
        self.modbus_socket.send(request)
        response = self.modbus_socket.recv(256)
        
        # Parse battery level (0-100%)
        if len(response) >= 9:
            battery_level = response[8]  # Example position
            self.update_battery_ui(battery_level)
            # Store in database
            self.db.update_battery_level(self.current_sensor['id'], battery_level)
    
    except Exception as e:
        print(f"Battery check error: {str(e)}")