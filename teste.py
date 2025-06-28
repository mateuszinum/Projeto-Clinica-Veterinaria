import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class JanelaImagem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carregar Imagem")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        # Label para exibir imagem
        self.label_imagem = QLabel("Nenhuma imagem carregada")
        self.label_imagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_imagem.setStyleSheet("border: 1px solid gray;")

        # Botão para carregar imagem
        self.botao_carregar = QPushButton("Carregar Imagem")
        self.botao_carregar.clicked.connect(self.carregar_imagem)

        self.layout.addWidget(self.label_imagem)
        self.layout.addWidget(self.botao_carregar)
        self.setLayout(self.layout)

    def carregar_imagem(self):
        nome_arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Imagem",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if nome_arquivo:
            pixmap = QPixmap(nome_arquivo)
            self.label_imagem.setPixmap(pixmap.scaled(
                self.label_imagem.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaImagem()
    janela.show()
    sys.exit(app.exec())
