import json
from PyQt6 import uic
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


app = QApplication([])


def carregar_pets():
    try:
        with open("pets.json", "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        with open("pets.json", "w", encoding="utf-8") as arquivo:
            json.dump([], arquivo)
        return []


def salvar_pets(pets):
    with open("pets.json", "w", encoding="utf-8") as arquivo:
        json.dump(pets, arquivo, indent=4, ensure_ascii=False)


class MinhaJanela(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("tela_recepcionista.ui", self)

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Checkbox", "Nome", "Peso", "Dono", "Raça"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.addBTN.clicked.connect(self.adicionarPet)
        self.editBTN.clicked.connect(self.editarPet)
        self.delBTN.clicked.connect(self.deletarPet)
        self.lineEdit.textChanged.connect(self.atualizar_interface)

    def abrir_formulario(self, pet=None):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Adicionar / Editar Pet")
        layout = QVBoxLayout()

        nome_input = QLineEdit()
        peso_input = QLineEdit()
        dono_input = QLineEdit()
        raca_input = QLineEdit()

        if pet:
            nome_input.setText(pet["nome"])
            peso_input.setText(pet["peso"])
            dono_input.setText(pet["dono"])
            raca_input.setText(pet["raca"])

        formulario = QFormLayout()
        formulario.addRow("Nome:", nome_input)
        formulario.addRow("Peso:", peso_input)
        formulario.addRow("Dono:", dono_input)
        formulario.addRow("Raça:", raca_input)

        botao_salvar = QPushButton("Salvar")
        layout.addLayout(formulario)
        layout.addWidget(botao_salvar)
        dialogo.setLayout(layout)

        def salvar():
            nome = nome_input.text().strip()
            peso = peso_input.text().strip()
            dono = dono_input.text().strip()
            raca = raca_input.text().strip()
            if not nome:
                QMessageBox.warning(dialogo, "Erro", "Nome não pode estar vazio.")
                return
            dialogo.accept()
            dialogo.resultado = {
                "nome": nome,
                "peso": peso,
                "dono": dono,
                "raca": raca
            }

        botao_salvar.clicked.connect(salvar)
        if dialogo.exec():
            return dialogo.resultado
        return None

    def atualizar_tabela(self, tabela, pets, filtro_nome):
        tabela.setRowCount(0)
        for pet in pets:
            if filtro_nome and filtro_nome.lower() not in pet["nome"].lower():
                continue
            linha = tabela.rowCount()
            tabela.insertRow(linha)

            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            tabela.setItem(linha, 0, checkbox_item)

            tabela.setItem(linha, 1, QTableWidgetItem(pet["nome"]))
            tabela.setItem(linha, 2, QTableWidgetItem(pet["peso"]))
            tabela.setItem(linha, 3, QTableWidgetItem(pet["dono"]))
            tabela.setItem(linha, 4, QTableWidgetItem(pet["raca"]))

    def linhas_marcadas(self):
        linhas = []
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if item.checkState() == Qt.CheckState.Checked:
                linhas.append(i)
        return linhas

    def adicionarPet(self):
        novo = self.abrir_formulario()
        if novo:
            todosPets.append(novo)
            salvar_pets(todosPets)
            self.atualizar_interface()

    def editarPet(self):
        linhas = self.linhas_marcadas()
        if len(linhas) != 1:
            QMessageBox.warning(self, "Erro", "Selecione exatamente 1 pet para editar.")
            return

        linha = linhas[0]
        pet_atual = todosPets[linha]
        atualizado = self.abrir_formulario(pet_atual)
        if atualizado:
            todosPets[linha] = atualizado
            salvar_pets(todosPets)
            self.atualizar_interface()

    def deletarPet(self):
        linhas = self.linhas_marcadas()
        if not linhas:
            QMessageBox.warning(self, "Erro", "Selecione pelo menos 1 pet para excluir.")
            return

        resposta = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir os pets selecionados?")
        if resposta == QMessageBox.StandardButton.Yes:
            for linha in sorted(linhas, reverse=True):
                todosPets.pop(linha)
            salvar_pets(todosPets)
            self.atualizar_interface()

    def atualizar_interface(self):
        self.atualizar_tabela(self.table, todosPets, self.lineEdit.text())


todosPets = carregar_pets()
janela = MinhaJanela()
janela.atualizar_interface()
janela.show()
app.exec()