from PyQt6.QtWidgets import QApplication, QMainWindow, QCalendarWidget
from PyQt6.QtGui import QTextCharFormat, QFont, QColor
from PyQt6.QtCore import QDate
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        calendar = QCalendarWidget(self)
        self.setCentralWidget(calendar)

        # # Create a format
        # format = QTextCharFormat()
        # format.setForeground(QColor("red"))
        # format.setFontWeight(QFont.Weight.Bold)

        # # Apply to a specific date
        # date = QDate(2025, 6, 21)  # June 21, 2025
        # calendar.setDateTextFormat(date, format)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())