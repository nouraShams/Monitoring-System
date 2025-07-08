# main.py
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from login_window import LoginWindow
from database import initialize_database

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    QMessageBox.critical(
        None,
        "Unhandled Exception",
        f"An unexpected error occurred:\n\n{str(exc_value)}",
        QMessageBox.Ok
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

if __name__ == "__main__":
    # Set up global exception handling
    sys.excepthook = handle_exception
    
    try:
        # Initialize the database
        initialize_database()
        
        # Create application
        app = QApplication(sys.argv)
        
        # Set application style and palette
        app.setStyle('Fusion')
        
        # Create and show login window
        window = LoginWindow()
        window.show()
        
        # Start application event loop
        sys.exit(app.exec())
        
    except Exception as e:
        QMessageBox.critical(
            None,
            "Initialization Error",
            f"Failed to initialize application:\n\n{str(e)}",
            QMessageBox.Ok
        )
        sys.exit(1)