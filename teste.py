from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import sys

class TelaSenha(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campo com Olhinho")

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText("Digite sua senha")

        self.botao_olho = QPushButton("👁")
        self.botao_olho.setCheckable(True)
        self.botao_olho.setCursor(Qt.CursorShape.PointingHandCursor)
        self.botao_olho.setFixedWidth(30)
        self.botao_olho.setStyleSheet("border: none;")

        self.botao_olho.toggled.connect(self.toggle_senha)

        layout = QHBoxLayout()
        layout.addWidget(self.senha_input)
        layout.addWidget(self.botao_olho)
        self.setLayout(layout)

    def toggle_senha(self, checked):
        if checked:
            self.senha_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.botao_olho.setText("🙈")  # muda o ícone se quiser
        else:
            self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.botao_olho.setText("👁")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaSenha()
    janela.show()
    sys.exit(app.exec())
