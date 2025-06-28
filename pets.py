import json
from PyQt6 import uic
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
import re


app = QApplication([])


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
        else:
            self.tela_registrar.resetaJanela()
        self.tela_registrar.show()
        self.hide()


class TelaLogin(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_login.ui", self)

        self.tela_inicial = tela_inicial

        self.login_input.textChanged.connect(self.formatarCPF)
        self.validarBTN.clicked.connect(self.validarDados)
        self.revelarBTN.clicked.connect(self.revelaSenha)

    def formatarCPF(self, texto):
        numeros = re.sub(r'\D', '', texto)
        tam = len(numeros)
        numeros = numeros[:11]
        novo_texto = ""

        if tam > 0:
            novo_texto += numeros[:3]

        if tam > 3:
            novo_texto += '.' + numeros[3:6]

        if tam > 6:
            novo_texto += '.' + numeros[6:9]

        if tam > 9:
            novo_texto += '-' + numeros[9:11]

        self.login_input.blockSignals(True)
        self.login_input.setText(novo_texto)
        self.login_input.blockSignals(False)

    def revelaSenha(self):
        if self.senha_input.echoMode() == QLineEdit.EchoMode.Password:
            self.senha_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)

    def validarDados(self):
        login_text = self.login_input.text()
        senha_text = self.senha_input.text()

        self.login_input.setStyleSheet("" if login_text else "border: 2px solid #e74c3c;")
        self.labelWarning1.setText("" if login_text else "Preencha o campo de login")
        self.senha_input.setStyleSheet("" if senha_text else "border: 2px solid #e74c3c;")
        self.labelWarning2.setText("" if senha_text else "Preencha o campo de senha")
        
        if login_text and senha_text:
            # valida dados no banco de dados
            self.openTelaProfissao()

            # if not valida_dados:
            #     self.login_input.setStyleSheet("border: 2px solid #e74c3c;")
            #     self.labelWarning1.setText("")
            #     self.senha_input.setStyleSheet("border: 2px solid #e74c3c;")
            #     self.labelWarning2.setText("Login ou senha inválidos")

    def openTelaProfissao(self):
        # checa qual é a profissão da pessoa e abre a tela correta
        self.tela_consulta = TelaConsulta()
        self.tela_consulta.show()
        self.hide()

    def closeEvent(self, event):
        self.tela_inicial.show()
        super().closeEvent(event)


class TelaRegistrar(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_registrar.ui", self)

        self.tela_inicial = tela_inicial

        self.telefone_input.textChanged.connect(self.formatar_telefone)
        self.cpf_input.textChanged.connect(self.formatar_cpf)
        self.revelarBTN1.clicked.connect(self.revelaSenha)
        self.revelarBTN2.clicked.connect(self.revelaConfirmarSenha)

        self.recepcionista_check_input.clicked.connect(lambda: self.veterinario_check_input.setChecked(False))
        self.veterinario_check_input.clicked.connect(lambda: self.recepcionista_check_input.setChecked(False))

        self.registrarBTN.clicked.connect(self.checaDados)

    # def printar_valor(self):
    #     nome = self.nome_input.text()
    #     data = self.data_input.date().toString("dd/MM/yyyy")
        
    #     print(nome, data)

    def formatar_telefone(self, texto):
        numeros = re.sub(r'\D', '', texto)[:11]
        tam = len(numeros)
        novo_texto = ""

        if tam >= 1:
            novo_texto += "(" + numeros[:2]

        if tam >= 3:
            novo_texto += ') ' + numeros[2]

        if tam >= 4:
            novo_texto += ' ' + numeros[3:7]

        if tam >= 8:
            novo_texto += '-' + numeros[7:11]

        self.telefone_input.blockSignals(True)
        self.telefone_input.setText(novo_texto)
        self.telefone_input.blockSignals(False)            

    def formatar_cpf(self, texto):
        numeros = re.sub(r'\D', '', texto)
        tam = len(numeros)
        numeros = numeros[:11]
        novo_texto = ""

        if tam > 0:
            novo_texto += numeros[:3]

        if tam > 3:
            novo_texto += '.' + numeros[3:6]

        if tam > 6:
            novo_texto += '.' + numeros[6:9]

        if tam > 9:
            novo_texto += '-' + numeros[9:11]

        self.cpf_input.blockSignals(True)
        self.cpf_input.setText(novo_texto)
        self.cpf_input.blockSignals(False)
        
    def revelaSenha(self):
        if self.senha_input.echoMode() == QLineEdit.EchoMode.Password:
            self.senha_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def revelaConfirmarSenha(self):
        if self.confirmar_senha_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirmar_senha_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.confirmar_senha_input.setEchoMode(QLineEdit.EchoMode.Password)

    # def registrar(self):
    #     nome = self.nome_input.text()
    #     data = self.data_input.date().toString("dd/MM/yyyy")
    #     telefone = self.telefone_input.text()
    #     cpf = self.cpf_input.text()
    #     email = self.email_input.text()
    #     senha = self.senha_input.text()
    #     confirmar_senha = self.confirmar_senha_input.text()
        # cargo_id

        # def definir_cargo(self):
        #     if self.recepcionista_check_input: Arrumar

    def checaDados(self):
        dados = {
            "nome": self.nome_input.text(), "data": self.data_input.date().toString("dd/MM/yyyy"),
            "telefone": self.telefone_input.text(), "cpf": self.cpf_input.text(),
            "email": self.email_input.text(), "recepcionista": self.recepcionista_check_input.isChecked(),
            "veterinario": self.veterinario_check_input.isChecked(), "senha": self.senha_input.text(),
            "confirmar_senha": self.confirmar_senha_input.text()
        }

        if self.validaDados(dados):
            pass
            # conecta no banco de dados e adiciona o usuário

            # self.tela_inicial.show()
            # self.hide()
    
    def validaDados(self, dados): # falta validar as coisas
        campos = {
            "nome": (dados["nome"], self.nome_input, self.labelWarning1),
            "telefone": (dados["telefone"], self.telefone_input, self.labelWarning2),
            "cpf": (dados["cpf"], self.cpf_input, self.labelWarning3),
            "email": (dados["email"], self.email_input, self.labelWarning4)
        }
        valido = True

        for campo, (valor, widget, warning) in campos.items():
            if not valor:
                widget.setStyleSheet("border: 2px solid #e74c3c;")
                warning.setText("Preencha o campo")
                valido = False
            else:
                if campo == "cpf" or campo == "email" or campo == "telefone" or campo == "senha":
                    pass
                    # funcoes que validam cada coisa

                widget.setStyleSheet("")
                warning.setText("")
    
        if not dados["recepcionista"] and not dados["veterinario"]:
            self.labelWarning7.setText("Escolha um cargo")
            valido = False
        else:
            self.labelWarning7.setText("")

        if (not dados["senha"] or not dados["confirmar_senha"]) or dados["senha"] != dados["confirmar_senha"]:
            self.senha_input.setStyleSheet("border: 2px solid #e74c3c;")
            self.confirmar_senha_input.setStyleSheet("border: 2px solid #e74c3c;")
            self.labelWarning5.setText("As senhas não coincidem")
            self.labelWarning6.setText("As senhas não coincidem")
            valido = False
        else:
            self.senha_input.setStyleSheet("")
            self.confirmar_senha_input.setStyleSheet("")
            self.labelWarning5.setText("")
            self.labelWarning6.setText("")
        
        return valido

    def resetaJanela(self):
        for widget in self.findChildren(QLineEdit): widget.clear(); widget.setStyleSheet("")
        for widget in self.findChildren(QLabel):
            if "labelWarning" in widget.objectName(): widget.setText("")
        self.data_input.setDate(QDate(2000, 1, 1))
        self.recepcionista_check_input.setChecked(False); self.veterinario_check_input.setChecked(False)

    def closeEvent(self, event):
        self.tela_inicial.show()
        super().closeEvent(event)


class TelaConsulta(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("tela_recepcionista_consulta.ui", self)
        
        self.petsBTN.clicked.connect(self.openTelaPet)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)
        self.sairBTN.clicked.connect(self.logout)

        opcoes = ["Almeida", "Beto", "Ciclano"]
        completer = QCompleter(opcoes, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.tutorInput.setCompleter(completer)

    def openTelaPet(self):
        self.tela_pet = TelaPet()
        self.tela_pet.show()
        self.hide()

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor()
        self.tela_tutor.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


class TelaTutor(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("tela_recepcionista_Tutor.ui", self)
        
        self.petsBTN.clicked.connect(self.openTelaPet)
        self.consultasBTN.clicked.connect(self.openTelaConsulta)
        self.sairBTN.clicked.connect(self.logout)

        self.addPetBTN.clicked.connect(self.adicionarTutor)
        self.editPetBTN.clicked.connect(self.editarTutor)
        self.delPetBTN.clicked.connect(self.deletarTutor)
        self.lineEdit.textChanged.connect(self.atualizarTabela)

        self.configurar_tabela()
        self.atualizar_tabela()

    def configurar_tabela(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Nome', 'Telefone', 'CPF'])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def atualizar_tabela(self):
        # conecta no banco de dados e busca todos os tutores
        row = 0
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem('id'))
        self.table.setItem(row, 1, QTableWidgetItem('nome'))
        self.table.setItem(row, 2, QTableWidgetItem('telefone'))
        self.table.setItem(row, 3, QTableWidgetItem('cpf'))
        self.table.setItem(row, 4, QTableWidgetItem('?'))

    # adicionar, editar e deletar tutor


    def openTelaPet(self):
        self.tela_pet = TelaPet()
        self.tela_pet.show()
        self.hide()

    def openTelaConsulta(self):
        self.tela_consulta = TelaConsulta()
        self.tela_consulta.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()
        

class TelaPet(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("tela_recepcionista_pet.ui", self)
        
        self.addPetBTN.clicked.connect(self.adicionarPet)
        self.editPetBTN.clicked.connect(self.editarPet)
        self.delPetBTN.clicked.connect(self.deletarPet)
        self.sairBTN.clicked.connect(self.logout)

        self.consultasBTN.clicked.connect(self.openTelaConsulta)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)

        self.petInput.textChanged.connect(self.atualizarTabela)

        self.configurarTabela()
        self.atualizarTabela()

    def configurarTabela(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome do Pet", "Raça", "Nome do Tutor"])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # essa função que faz a tabela mudar toda vez que procura por um pet, conectar com o banco de dados
    def atualizarTabela(self):
        filtro = self.petInput.text()

        # conecta no banco de dados e busca os pets com o filtro
        pets = 'variavel com todos os pets'

        # self.table.setRowCount(0)
        # for pet in pets:
        #     linha = self.table.rowCount()
        #     self.table.insertRow(linha)
        #     self.table.setItem(linha, 0, QTableWidgetItem(pet["nome"]))
        #     self.table.setItem(linha, 1, QTableWidgetItem(pet["peso"]))
        #     self.table.setItem(linha, 2, QTableWidgetItem(pet["dono"]))
        #     self.table.setItem(linha, 3, QTableWidgetItem(pet["raca"]))

    def getPetSelecionadoID(self):
        linhas = self.table.selectionModel().selectedRows()
        if len(linhas) != 1:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione exatamente um pet.")
            return None
        return int(self.table.item(linhas[0].row(), 0).text())

    def abrirFormulario(self, pet=None):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(f"{'Editar' if pet else 'Adicionar'} Pet")
        layout = QVBoxLayout()

        nome_input = QLineEdit()
        peso_input = QLineEdit()
        raca_input = QLineEdit()
        tutor_input = QComboBox()

        if pet:
            nome_input.setText(pet["nome"])
            peso_input.setText(pet["peso"])
            # acessa banco de dados e adiciona todos os tutores com um for
            # tutor_input.addItem(f'tutor['Nome'] (tutor['ID'])')
            raca_input.setText(pet["raca"])

        formulario = QFormLayout()
        formulario.addRow("Nome:", nome_input)
        formulario.addRow("Peso:", peso_input)
        formulario.addRow("Dono:", tutor_input)
        formulario.addRow("Raça:", raca_input)

        botao_salvar = QPushButton("Salvar")
        layout.addLayout(formulario)
        layout.addWidget(botao_salvar)
        dialogo.setLayout(layout)

        def salvar():
            nome = nome_input.text().strip()
            peso = peso_input.text().strip()
            # dono = tutor_input.currentText().strip()
            raca = raca_input.text().strip()
            if not nome:
                QMessageBox.warning(dialogo, "Erro", "Nome não pode estar vazio.")
                return
            dialogo.accept()
            dialogo.resultado = {
                "nome": nome,
                "peso": peso,
                "dono": 'PLACEHOLDER',
                "raca": raca
            }

        botao_salvar.clicked.connect(salvar)
        if dialogo.exec():
            return dialogo.resultado
        return None

    def adicionarPet(self):
        dados_pet = self.abrirFormulario()
        if dados_pet:
            # conecta no bando de dados e adiciona o pet

            self.atualizarTabela()

    def editarPet(self):
        pet_id = self.getPetSelecionadoID()
        
        # seleciona o pet no banco de dados
        pet_atual = 'PLACEHOLDER'
        atualizado = self.abrirFormulario(pet_atual)
        if atualizado:

            self.atualizarTabela()

    def deletarPet(self):
        linhas = self.table.selectionModel().selectedRows()
        if len(linhas) == 0:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos um pet.")
            return
        resposta = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir os pets selecionados?")
        if resposta == QMessageBox.StandardButton.Yes:
            for linha in sorted(linhas, reverse=True):
                pass
                # deleta o pet do banco de dados
            self.atualizarTabela()

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor()
        self.tela_tutor.show()
        self.hide()
    
    def openTelaConsulta(self):
        self.tela_consulta = TelaConsulta()
        self.tela_consulta.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


janela = TelaInicial()
janela.show()
app.exec()