# login_window.py
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush
from database import MonitoringDB  # Import the database class
from DashboardWindow import DashboardWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security System Login")
        self.resize(400, 300)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Gradient background
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
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Styled frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        layout.addWidget(frame)
        
        # Title
        title = QLabel("SECURITY SYSTEM")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e3c72;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Please login to continue")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #1e3c72;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(subtitle)
        
        # Username field
        username_container = QWidget()
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)
        
        username_label = QLabel("Username")
        username_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        username_label.setStyleSheet("color: #555555;")
        username_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        username_layout.addWidget(self.username_input)
        frame_layout.addWidget(username_container)
        
        # Password field
        password_container = QWidget()
        password_layout = QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        password_label = QLabel("Password")
        password_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        password_label.setStyleSheet("color: #555555;")
        password_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        password_layout.addWidget(self.password_input)
        frame_layout.addWidget(password_container)
        
        # Login button
        self.login_button = QPushButton("LOGIN")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 0;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1d6fa5;
            }
        """)
        self.login_button.clicked.connect(self.authenticate)
        frame_layout.addWidget(self.login_button)
        
        # Error message placeholder
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        frame_layout.addWidget(self.error_label)
        
        # Database connection
        self.db = MonitoringDB()
        
        # Fade-in animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
    
    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        user = self.db.authenticate_user(username, password)
        if user:
            # Close the database connection for this window
            self.db.close()
            
            # Open the dashboard
            self.dashboard = DashboardWindow(user)
            self.dashboard.show()
            self.close()
        else:
            self.show_error("Invalid username or password")
    
    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        
        # Clear inputs
        self.password_input.clear()
        
        # Shake animation for error feedback
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(100)
        animation.setLoopCount(2)
        animation.setKeyValueAt(0, self.pos())
        animation.setKeyValueAt(0.25, self.pos() + Qt.Point(10, 0))
        animation.setKeyValueAt(0.5, self.pos() + Qt.Point(-10, 0))
        animation.setKeyValueAt(0.75, self.pos() + Qt.Point(10, 0))
        animation.setEndValue(self.pos())
        animation.start()
    
    def closeEvent(self, event):
        # Ensure database connection is closed
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())