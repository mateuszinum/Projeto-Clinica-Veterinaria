import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QWidget, QVBoxLayout, QLabel, QAbstractItemView
)

class NovaJanela(QWidget):
    def __init__(self, linha, valores):
        super().__init__()
        self.setWindowTitle("Detalhes da Linha")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Linha: {linha}"))
        layout.addWidget(QLabel(f"Valores: {valores}"))
        self.setLayout(layout)

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tabela com Seleção de Linha")

        self.tabela = QTableWidget(5, 3)
        self.setCentralWidget(self.tabela)

        # Preencher a tabela
        for i in range(5):
            for j in range(3):
                self.tabela.setItem(i, j, QTableWidgetItem(f"Célula {i},{j}"))

        # Configurar seleção de linha
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Conectar sinal de duplo clique
        self.tabela.cellDoubleClicked.connect(self.abrir_nova_janela)

    def abrir_nova_janela(self, linha, _coluna):
        # Obter os valores da linha inteira
        valores = []
        for col in range(self.tabela.columnCount()):
            item = self.tabela.item(linha, col)
            valores.append(item.text() if item else "")

        self.nova_janela = NovaJanela(linha, valores)
        self.nova_janela.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())
