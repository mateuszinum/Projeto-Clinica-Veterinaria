import re
import os
import shutil
from PyQt6 import uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QDate
import sqlite3
import bcrypt
import perfis as p

FOTOS_TUTORES_DIR = 'fotos_tutores'
if not os.path.exists(FOTOS_TUTORES_DIR):
    os.makedirs(FOTOS_TUTORES_DIR)


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
        self.perfil = None
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
            valida_dados = False

            conexao = sqlite3.connect('dados.db')
            cursor = conexao.cursor()

            cursor.execute(f"SELECT Email, Senha FROM Perfis")

            dados = cursor.fetchall()

            senha_bytes = senha_text.encode('utf-8')
            salt = bcrypt.gensalt()
            hash_senha = bcrypt.hashpw(senha_bytes, salt)
                
            for email, senha in dados:
                if email == login_text and senha == hash_senha:
                    valida_dados = True
                    cursor.execute("SELECT * FROM Perfis WHERE Email = ? AND Senha = ?", (email, senha))
                    perfil = cursor.fetchall()
                    self.perfil = p.Perfil(perfil["Nome"], senha_text, perfil["Cargo_ID"], perfil["Data_Nasc"], perfil["CPF"], perfil["Email"])
                    self.openTelaProfissao()


            if not valida_dados:
                self.login_input.setStyleSheet("border: 2px solid #e74c3c;")
                self.labelWarning1.setText("")
                self.senha_input.setStyleSheet("border: 2px solid #e74c3c;")
                self.labelWarning2.setText("Login ou senha inválidos")



    def openTelaProfissao(self):
        if self.perfil.cargo_id == 1:
            #Abri Tela recepcionista
            pass
        else:
            #Abrir tela medico
            pass
        self.tela_consulta = TelaConsulta(self.tela_inicial)
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

    def formatar_telefone(self, texto):
        numeros = re.sub(r'\D', '', texto)[:11]
        tam = len(numeros)
        novo_texto = ""

        if tam >= 1:
            novo_texto += "(" + numeros[:2]

        if tam >= 3:
            novo_texto += ') ' + numeros[2:7]

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

    def checaDados(self):
        dados = {
            "nome": self.nome_input.text(), "data": self.data_input.date().toString("dd/MM/yyyy"),
            "telefone": self.telefone_input.text(), "cpf": self.cpf_input.text(),
            "email": self.email_input.text(), "recepcionista": self.recepcionista_check_input.isChecked(),
            "veterinario": self.veterinario_check_input.isChecked(), "senha": self.senha_input.text(),
            "confirmar_senha": self.confirmar_senha_input.text()
        }

        if self.validaDados(dados):
            
            
            
            # Depois de verificar td certinho faz esse proximo passo aq, como n sei exatamente como tu vai fazer, 
            # deixei aq pra tu completar depois
            # mas qualquer coisa eu faço depois q tu terminar
            # perfil = p.Perfil() # Coloca nos paramentros, nome, senha, o id do cargo(recepcionista = 1, medico = 2), data_nasc, cpf, email
            # perfil.salvar_dados()
            QMessageBox.information(self, "Sucesso", "Usuário registrado com sucesso!")
            self.tela_inicial.show()
            self.close()
    
    def validaDados(self, dados):
        campos = {
            "nome": (dados["nome"], self.nome_input, self.labelWarning1, None),
            "telefone": (dados["telefone"], self.telefone_input, self.labelWarning2, self.validar_telefone),
            "cpf": (dados["cpf"], self.cpf_input, self.labelWarning3, self.validar_cpf),
            "email": (dados["email"], self.email_input, self.labelWarning4, self.validar_email)
        }
        valido = True

        for campo, (valor, widget, warning, funcao_validacao) in campos.items():
            if not valor:
                widget.setStyleSheet("border: 2px solid #e74c3c;")
                warning.setText("Preencha o campo")
                valido = False

            elif funcao_validacao and not funcao_validacao(valor):
                widget.setStyleSheet("border: 2px solid #e74c3c;")

                if campo == 'cpf':
                    warning.setText("CPF inválido")
                elif campo == 'telefone':
                    warning.setText("Telefone inválido")
                elif campo == 'email':
                    warning.setText("Formato de e-mail inválido")

                valido = False
            else:
                widget.setStyleSheet("")
                warning.setText("")

        if not dados["recepcionista"] and not dados["veterinario"]:
            self.labelWarning7.setText("Escolha um cargo")
            valido = False
        else:
            self.labelWarning7.setText("")

        resultado_validacao, mensagem_validacao = self.validar_senha(dados["senha"])
        if not resultado_validacao:
            self.senha_input.setStyleSheet("border: 2px solid #e74c3c;")
            self.confirmar_senha_input.setStyleSheet("border: 2px solid #e74c3c;")
            self.labelWarning5.setText(mensagem_validacao)
            self.labelWarning6.setText("")
            valido = False

        elif dados["senha"] != dados["confirmar_senha"]:
            self.senha_input.setStyleSheet("border: 2px solid #e74c3c;")
            self.confirmar_senha_input.setStyleSheet("border: 2px solid #e74c3c;")
            self.labelWarning5.setText("As senhas não coincidem")
            self.labelWarning6.setText("As senhas não coincidem")
            valido = False

        else:
            if dados["senha"]:
                self.senha_input.setStyleSheet("")
                self.confirmar_senha_input.setStyleSheet("")
                self.labelWarning5.setText("")
                self.labelWarning6.setText("")
        
        return valido

    def validar_cpf(self, cpf):
        return len(cpf) == 14

    def validar_telefone(self, telefone):
        return len(telefone) == 15

    def validar_email(self, email):
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None

    def validar_senha(self, senha):
        mensagem = ""
        valido = True
        if len(senha) < 8:
            mensagem += "A senha deve ter pelo menos 8 caracteres."
            valido = False
        if not re.search(r'[A-Z]', senha):
            mensagem += "\nA senha deve conter pelo menos uma letra maiúscula."
            valido = False
        if not re.search(r'[a-z]', senha):
            mensagem += "\nA senha deve conter pelo menos uma letra minúscula."
            valido = False
        if not re.search(r'\d', senha):
            mensagem += "\nA senha deve conter pelo menos um número."
            valido = False
        if not re.search(r'[\W_]', senha):
            mensagem += "\nA senha deve conter pelo menos um símbolo especial."
            valido = False
        
        if not valido:
            return False, mensagem
    
        return True, ""

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
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_recepcionista_consulta.ui", self)
        
        self.tela_inicial = tela_inicial

        self.petsBTN.clicked.connect(self.openTelaPet)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)
        self.sairBTN.clicked.connect(self.logout)

        opcoes = ["Almeida", "Beto", "Ciclano"]
        completer = QCompleter(opcoes, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.tutorInput.setCompleter(completer)

    def openTelaPet(self):
        self.tela_pet = TelaPet(self.tela_inicial)
        self.tela_pet.show()
        self.hide()

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor(self.tela_inicial)
        self.tela_tutor.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


class TelaTutor(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_recepcionista_Tutor.ui", self)
        
        self.tela_inicial = tela_inicial

        self.petsBTN.clicked.connect(self.openTelaPet)
        self.consultasBTN.clicked.connect(self.openTelaConsulta)
        self.sairBTN.clicked.connect(self.logout)

        self.addTutorBTN.clicked.connect(self.adicionarTutor)
        self.editTutorBTN.clicked.connect(self.editarTutor)
        self.delTutorBTN.clicked.connect(self.deletarTutor)
        self.tutorInput.textChanged.connect(self.atualizar_tabela)

        self.configurar_tabela()
        self.atualizar_tabela()

    def configurar_tabela(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Nome', 'Telefone', 'CPF', 'Foto Path'])
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(4, True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def atualizar_tabela(self):
        filtro = self.tutorInput.text()
        # conecta no banco de dados e busca tutores com o filtro
        tutores_db = [
            {'id': 1, 'nome': 'João da Silva', 'telefone': '(11) 98765-4321', 'cpf': '123.456.789-00', 'foto_path': 'fotos_tutores/1.jpg'},
            {'id': 2, 'nome': 'Maria Oliveira', 'telefone': '(21) 91234-5678', 'cpf': '111.222.333-44', 'foto_path': ''},
        ]

        self.table.setRowCount(0)
        for tutor in tutores_db:
            if filtro.lower() in tutor['nome'].lower():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(tutor['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(tutor['nome']))
                self.table.setItem(row, 2, QTableWidgetItem(tutor['telefone']))
                self.table.setItem(row, 3, QTableWidgetItem(tutor['cpf']))
                self.table.setItem(row, 4, QTableWidgetItem(tutor['foto_path']))

    def abrirFormularioTutor(self, tutor=None):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(f"{'Editar' if tutor else 'Adicionar'} Tutor")
        layout = QVBoxLayout()
        formulario = QFormLayout()

        nome_input = QLineEdit(tutor['nome'] if tutor else '')
        telefone_input = QLineEdit(tutor['telefone'] if tutor else '')
        cpf_input = QLineEdit(tutor['cpf'] if tutor else '')
        
        foto_layout = QHBoxLayout()
        foto_label = QLabel("Nenhuma foto selecionada")
        foto_preview = QLabel()
        foto_preview.setFixedSize(100, 100)
        foto_preview.setScaledContents(True)
        dialogo.foto_path = tutor['foto_path'] if tutor else ''
        
        if dialogo.foto_path and os.path.exists(dialogo.foto_path):
            foto_preview.setPixmap(QPixmap(dialogo.foto_path))
            foto_label.setText(os.path.basename(dialogo.foto_path))

        def selecionar_foto():
            fname, _ = QFileDialog.getOpenFileName(self, 'Selecionar Foto', '', 'Imagens (*.png *.jpg *.jpeg)')
            if fname:
                dialogo.foto_path = fname
                foto_preview.setPixmap(QPixmap(fname))
                foto_label.setText(os.path.basename(fname))

        botao_selecionar = QPushButton("Selecionar Foto")
        botao_selecionar.clicked.connect(selecionar_foto)
        foto_layout.addWidget(botao_selecionar)
        foto_layout.addWidget(foto_label)
        
        formulario.addRow("Nome:", nome_input)
        formulario.addRow("Telefone:", telefone_input)
        formulario.addRow("CPF:", cpf_input)

        layout.addLayout(formulario)
        layout.addWidget(foto_preview)
        layout.addLayout(foto_layout)
        
        botao_salvar = QPushButton("Salvar")
        layout.addWidget(botao_salvar)
        dialogo.setLayout(layout)

        def salvar():
            nome = nome_input.text().strip()
            telefone = telefone_input.text().strip()
            cpf = cpf_input.text().strip()

            if not nome or not telefone or not cpf:
                QMessageBox.warning(dialogo, "Erro", "Todos os campos devem ser preenchidos.")
                return


            novo_foto_path = dialogo.foto_path
            if dialogo.foto_path and not dialogo.foto_path.startswith(FOTOS_TUTORES_DIR):
                id_tutor = tutor['id'] if tutor else 'novo'
                ext = os.path.splitext(dialogo.foto_path)[1]
                novo_nome_arquivo = f"tutor_{id_tutor}_{QDate.currentDate().toString('yyyyMMdd')}{ext}"
                novo_foto_path = os.path.join(FOTOS_TUTORES_DIR, novo_nome_arquivo)
                shutil.copy(dialogo.foto_path, novo_foto_path)

            dialogo.resultado = {
                "nome": nome, "telefone": telefone, "cpf": cpf, "foto_path": novo_foto_path
            }
            dialogo.accept()

        botao_salvar.clicked.connect(salvar)
        if dialogo.exec():
            return dialogo.resultado
        return None

    def adicionarTutor(self):
        dados_tutor = self.abrirFormularioTutor()
        if dados_tutor:
            conexao = sqlite3.connect('dados.db')
            cursor = conexao.cursor()

            cursor.execute("INSERT INTO Tutores (Nome, Telefone, CPF, Foto_Path) VALUES (?, ?, ?, ?)", (dados_tutor["nome"], dados_tutor["telefone"], dados_tutor["cpf"], dados_tutor["foto_path"]))
            conexao.commit()

            QMessageBox.information(self, "Sucesso", "Tutor adicionado com sucesso!")
            self.atualizar_tabela()

    def editarTutor(self):
        linhas = self.table.selectionModel().selectedRows()
        if not linhas or len(linhas) != 1:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos um pet.")
            return

        tutor_atual = {
            'id': int(self.table.item(linhas.row(), 0).text()),
            'nome': self.table.item(linhas.row(), 1).text(),
            'telefone': self.table.item(linhas.row(), 2).text(),
            'cpf': self.table.item(linhas.row(), 3).text(),
            'foto_path': self.table.item(linhas.row(), 4).text()
        }
        
        dados_atualizados = self.abrirFormularioTutor(tutor_atual)
        if dados_atualizados:
            # conecta no banco de dados e atualiza o tutor

            QMessageBox.information(self, "Sucesso", "Tutor atualizado com sucesso!")
            self.atualizar_tabela()

    def deletarTutor(self):
        linhas = self.table.selectionModel().selectedRows()
        if not linhas or len(linhas) != 1:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos um pet.")
            return

        resposta = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir os tutores selecionados?")

        if resposta == QMessageBox.StandardButton.Yes:
            for linha in sorted(linhas, reverse=True):
                tutor_id = int(self.table.item(linha.row(), 0).text())
                # conecta no banco de dados e deleta o tutor_id

                # deleta a foto do tutor
                foto_path = self.table.item(linha, 4).text()
                if foto_path and os.path.exists(foto_path):
                    os.remove(foto_path)

            QMessageBox.information(self, "Sucesso", "Tutor deletado com sucesso!")
            self.atualizar_tabela()

    def openTelaPet(self):
        self.tela_pet = TelaPet(self.tela_inicial)
        self.tela_pet.show()
        self.hide()

    def openTelaConsulta(self):
        self.tela_consulta = TelaConsulta(self.tela_inicial)
        self.tela_consulta.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


class TelaPet(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_recepcionista_pet.ui", self)
        
        self.tela_inicial = tela_inicial

        # deletar isso dps
        self.pets_db = [
            {'id': 1, 'nome': 'Bolinha', 'raca': 'Poodle', 'id_tutor': 1, 'nome_tutor': 'João da Silva'},
            {'id': 2, 'nome': 'Fofinho', 'raca': 'Siamês', 'id_tutor': 2, 'nome_tutor': 'Maria Oliveira'},
            {'id': 3, 'nome': 'Rex', 'raca': 'Vira-lata', 'id_tutor': 1, 'nome_tutor': 'João da Silva'},
            {'id': 4, 'nome': 'Miau', 'raca': 'Persa', 'id_tutor': 2, 'nome_tutor': 'Maria Oliveira'},
            {'id': 5, 'nome': 'Trovão', 'raca': 'Golden Retriever', 'id_tutor': 1, 'nome_tutor': 'João da Silva'}
        ]

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

    def adicionarPet(self):
        dados_pet = self.abrirFormulario()
        if dados_pet:
            # conecta no banco de dados e adiciona o pet
            QMessageBox.information(self, "Sucesso", "Pet adicionado com sucesso!")
            self.atualizarTabela()

    def editarPet(self):
        linhas = self.table.selectionModel().selectedRows()
        if not linhas or len(linhas) != 1:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos um pet.")
            return
        
        # pet_atual = 'variável que busca o pet no banco de dados pelo ID selecionado'
        pet_atual = {"nome": "Rex", "peso": "10kg", "raca": "Vira-lata"}
        dados_atualizado = self.abrirFormulario(pet_atual)
        if dados_atualizado:
            # conecta no banco de dados e atualiza o pet
            QMessageBox.information(self, "Sucesso", "Pet atualizado com sucesso!")
            self.atualizarTabela()

    def deletarPet(self):
        linhas = self.table.selectionModel().selectedRows()
        if not linhas:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos um pet.")
            return
        resposta = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir os pets selecionados?")
        if resposta == QMessageBox.StandardButton.Yes:
            for linha in sorted(linhas, reverse=True):
                pet_id = int(self.table.item(linha.row(), 0).text())
                # conecta no banco de dados e deleta o pet pelo pet_id
            QMessageBox.information(self, "Sucesso", "Pet deletado com sucesso!")
            self.atualizarTabela()

    def atualizarTabela(self):
        filtro = self.petInput.text().lower()
        # conecta no banco de dados e busca pets com o filtro

        for pet in self.pets_db:
            if filtro in pet['nome'].lower() or filtro in pet['nome_tutor'].lower():
                linha = self.table.rowCount()
                self.table.insertRow(linha)

                self.table.setItem(linha, 0, QTableWidgetItem(str(pet["id"])))
                self.table.setItem(linha, 1, QTableWidgetItem(pet["nome"]))
                self.table.setItem(linha, 2, QTableWidgetItem(pet["raca"]))
                self.table.setItem(linha, 3, QTableWidgetItem(pet["nome_tutor"]))

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
            raca_input.setText(pet["raca"])
        
        # tutores = conecta no banco de dados e busca todos os tutores
        # for tutor in tutores():
        #     tutor_input.addItem(f'tutor['nome'] (tutor['id'])')

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
            raca = raca_input.text().strip()
            if not nome:
                QMessageBox.warning(dialogo, "Erro", "Nome não pode estar vazio.")
                return
            dialogo.accept()
            dialogo.resultado = {
                "nome": nome, "peso": peso, "raca": raca,
                # "id_tutor": 
            }

        botao_salvar.clicked.connect(salvar)
        if dialogo.exec():
            return dialogo.resultado
        return None

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor(self.tela_inicial)
        self.tela_tutor.show()
        self.hide()
    
    def openTelaConsulta(self):
        self.tela_consulta = TelaConsulta(self.tela_inicial)
        self.tela_consulta.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


janela = TelaInicial()
janela.show()
app.exec()