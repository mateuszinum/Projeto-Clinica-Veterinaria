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


class TelaInicial(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("tela_inicial.ui", self)

        self.tela_login = None
        self.loginBTN.clicked.connect(self.openTelaLogin)
        self.tela_registrar = None
        self.registrarBTN.clicked.connect(self.openTelaRegistrar)

    def openTelaLogin(self):
        if self.tela_login is None:
            self.tela_login = TelaLogin(self)
        self.tela_login.show()
        self.hide()

    def openTelaRegistrar(self):
        if self.tela_registrar is None:
            self.tela_registrar = TelaRegistrar(self)
        self.tela_registrar.show()
        self.hide()


class TelaLogin(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_login.ui", self)

        self.tela_inicial = tela_inicial
        self.validarBTN.clicked.connect(self.openTelaProfissao)

    def closeEvent(self, event):
        self.tela_inicial.show()
        super().closeEvent(event)

    def openTelaProfissao(self):
        self.tela_consulta = TelaConsulta()
        self.tela_consulta.show()
        self.hide()


class TelaRegistrar(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_registrar.ui", self)

        self.tela_inicial = tela_inicial
        self.registrarBTN.clicked.connect(self.validarANDsalvar)
        self.lineEdit_2.setPlaceholderText("Enter CPF")

    def closeEvent(self, event):
        self.tela_inicial.show()
        super().closeEvent(event)

    def validarANDsalvar(self):
        self.tela_inicial.show()
        self.hide()


class TelaConsulta(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("tela_recepcionista_consulta.ui", self)
        
        self.petsBTN.clicked.connect(self.openTelaPet)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)

    def openTelaPet(self):
        self.tela_pet = TelaPet()
        self.tela_pet.show()
        self.hide()

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor()
        self.tela_tutor.show()
        self.hide()


class TelaTutor(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("tela_recepcionista_Tutor.ui", self)
        
        self.petsBTN.clicked.connect(self.openTelaPet)
        self.consultasBTN.clicked.connect(self.openTelaConsulta)

    def openTelaPet(self):
        self.tela_pet = TelaPet()
        self.tela_pet.show()
        self.hide()

    def openTelaConsulta(self):
        self.tela_consulta = TelaConsulta()
        self.tela_consulta.show()
        self.hide()
        

class TelaPet(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("tela_recepcionista_pet.ui", self)

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["✔", "Nome", "Peso", "Dono", "Raça"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.addPetBTN.clicked.connect(self.adicionarPet)
        self.editPetBTN.clicked.connect(self.editarPet)
        self.delPetBTN.clicked.connect(self.deletarPet)

        self.consultasBTN.clicked.connect(self.openTelaConsulta)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)

        self.lineEdit.textChanged.connect(self.atualizar_interface)

        self.atualizar_interface()

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor()
        self.tela_tutor.show()
        self.hide()
    
    def openTelaConsulta(self):
        self.tela_consulta = TelaConsulta()
        self.tela_consulta.show()
        self.hide()

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
janela = TelaInicial()
janela.show()
app.exec()