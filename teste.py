from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QCalendarWidget,
    QVBoxLayout, QDialog, QLabel
)
from PyQt6.QtCore import QDate, Qt
import sys

class CalendarioPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Data")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(300, 250)

        self.calendario = QCalendarWidget(self)
        self.calendario.clicked.connect(self.data_selecionada)

        layout = QVBoxLayout(self)
        layout.addWidget(self.calendario)

        self.data = None

    def data_selecionada(self, date: QDate):
        self.data = date
        self.accept()  # fecha o popup


class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Botão com Lupa e Calendário")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        # Botão com emoji de lupa
        self.botao_lupa = QPushButton("🔍 Selecionar Data")
        self.botao_lupa.clicked.connect(self.abrir_calendario)

        # Label para mostrar a data selecionada
        self.label_data = QLabel("Nenhuma data selecionada")
        self.label_data.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.botao_lupa)
        layout.addWidget(self.label_data)

        # Aqui será "salva" a data (como variável interna)
        self.data_selecionada = None

    def abrir_calendario(self):
        popup = CalendarioPopup(self)
        if popup.exec():  # Quando o calendário for fechado com "accept"
            self.data_selecionada = popup.data
            self.label_data.setText(f"Data selecionada: {self.data_selecionada.toString('dd/MM/yyyy')}")
            print("Data salva:", self.data_selecionada)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())