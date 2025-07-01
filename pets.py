import re
import os
import bcrypt
import shutil
import sqlite3
import perfis as p
from PyQt6 import uic
from PyQt6.QtWidgets import *
from datetime import datetime
from PyQt6.QtGui import QPixmap, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt, QDate


conexao = sqlite3.connect('dados.db')
cursor = conexao.cursor()


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
        
        self.tela_login.resetaJanela()
        
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

        self.validarBTN.clicked.connect(self.validarDados)
        self.revelarBTN.clicked.connect(self.revelaSenha)

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

            cursor.execute(f"SELECT Email, Senha_Hash FROM Perfis")

            dados = cursor.fetchall()

            senha_bytes = senha_text.encode('utf-8')

            for email, senha in dados:
                if email == login_text and bcrypt.checkpw(senha_bytes, senha):
                    valida_dados = True
                    cursor.execute("SELECT * FROM Perfis WHERE Email = ? AND Senha_Hash = ?", (email, senha))
                    perfil = cursor.fetchall()[0]
                    self.perfil = p.Perfil(perfil[1], senha_text, perfil[6], perfil[2], perfil[3], perfil[4])
                    self.openTelaProfissao()

            if not valida_dados:
                self.login_input.setStyleSheet("border: 2px solid #e74c3c;")
                self.labelWarning1.setText("")
                self.senha_input.setStyleSheet("border: 2px solid #e74c3c;")
                self.labelWarning2.setText("Login ou senha inválidos")

    def openTelaProfissao(self):
        if self.perfil.cargo_id == 1:
            self.tela_consulta = TelaConsulta(self.tela_inicial)
            self.tela_consulta.show()
            self.hide()
        else:
            self.tela_veterinario = TelaVeterinario(self.tela_inicial)
            self.tela_veterinario.show()
            self.hide()

    def resetaJanela(self):
        self.login_input.clear()
        self.senha_input.clear()
        
        self.labelWarning1.setText("")
        self.labelWarning2.setText("")

        self.login_input.setStyleSheet("")
        self.senha_input.setStyleSheet("")

        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)

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
            "nome": self.nome_input.text(), 
            "data": self.data_input.date().toString("dd/MM/yyyy"),
            "telefone": self.telefone_input.text(), 
            "cpf": self.cpf_input.text(),
            "email": self.email_input.text(), 
            "recepcionista": self.recepcionista_check_input.isChecked(),
            "veterinario": self.veterinario_check_input.isChecked(), 
            "senha": self.senha_input.text(),
            "confirmar_senha": self.confirmar_senha_input.text()
        }

        if self.validaDados(dados):

            cargo_id = 1 if dados["recepcionista"] else 2
            perfil = p.Perfil(dados["nome"], dados["senha"], cargo_id, dados["data"], dados["cpf"], dados["email"])
            perfil.salvar_dados()
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
        self.datas_marcadas = set()

        self.formato_data_consulta = QTextCharFormat()
        self.formato_data_consulta.setForeground(QColor("red"))
        self.formato_data_consulta.setFontWeight(QFont.Weight.Bold)

        self.addConsultaBTN.clicked.connect(self.adicionarConsulta)
        self.editConsultaBTN.clicked.connect(self.editarConsulta)
        self.delConsultaBTN.clicked.connect(self.deletarConsulta)

        self.petsBTN.clicked.connect(self.openTelaPet)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)
        self.sairBTN.clicked.connect(self.logout)

    def adicionarConsulta(self):
        dados_consulta = self.abrirFormularioConsulta()
        print(dados_consulta)

    def editarConsulta(self):
        pass

    def deletarConsulta(self):
        pass

    def abrirFormularioConsulta(self, consulta=None):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(f"{'Editar' if consulta else 'Adicionar'} Consulta")
        dialogo.setStyleSheet("background-color: #93cbd9;")

        layout = QVBoxLayout()
        formulario = QFormLayout()

        tutor_input = QLineEdit()
        tutores = 'variavel com todos os tutores do banco de dados'
        tutor_nomes = list(tutores)
        completer = QCompleter(tutor_nomes)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        tutor_input.setCompleter(completer)
        if consulta:
            tutor_input.setText(consulta['tutor'])

        pet_input = QComboBox()
        if consulta:
            pets_do_tutor = 'pega os pets de consulta["tutor"]'
            pet_input.addItems(pets_do_tutor)
            pet_input.setCurrentText(consulta['pet'])

        def atualizar_pets():
            nome_tutor = tutor_input.text().strip()
            pets = 'pega todos os pets do tutor'
            pet_input.clear()
            pet_input.addItems(pets)

        tutor_input.editingFinished.connect(atualizar_pets)

        data_label = QLabel("Nenhuma data selecionada")
        data_selecionada = {"valor": None}

        botao_lupa = QPushButton("🔍 Selecionar Data")
        botao_lupa.setStyleSheet(
            'background-color: #2f80ed; color: white; padding: 6px 12px; border-radius: 4px; '
            'border: none; font-size: 14px; font-weight: bold;'
            )
        def escolher_data():
            data = self.abrir_calendario()
            if data:
                data_label.setText(f"Data Selecionada - {data}")
                data_selecionada["valor"] = data
        botao_lupa.clicked.connect(escolher_data)

        if consulta:
            if 'data' in consulta:
                data_label.setText(f"Data Selecionada - {consulta['data']}")
                data_selecionada["valor"] = consulta['data']

        formulario.addRow("Tutor:", tutor_input)
        formulario.addRow("Pet:", pet_input)
        formulario.addRow("Data:", botao_lupa)
        layout.addLayout(formulario)
        layout.addWidget(data_label)

        botao_salvar = QPushButton("Salvar")
        botao_salvar.setStyleSheet(
            'background-color: #27ae60; color: white; padding: 6px 12px; border-radius: 4px; '
            'border: none; font-size: 14px; font-weight: bold;'
        )
        layout.addWidget(botao_salvar)

        dialogo.setLayout(layout)

        def salvar():
            data = data_selecionada["valor"]
            tutor = tutor_input.text().strip()
            pet = pet_input.currentText().strip()

            if not data or not tutor or not pet:
                QMessageBox.warning(dialogo, "Erro", "Todos os campos devem ser preenchidos.")
                return

            dialogo.resultado = {
                "data": data,
                "tutor": tutor,
                "pet": pet
            }
            dialogo.accept()

        botao_salvar.clicked.connect(salvar)

        if dialogo.exec():
            return dialogo.resultado
        return None
    
    def abrir_calendario(self):
        popup = CalendarioPopup(self)
        if popup.exec():
            return popup.data.toString('dd/MM/yyyy')

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
        self.accept()


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

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def atualizar_tabela(self):
        filtro = self.tutorInput.text().strip()

        if len(filtro) == 0:
            cursor.execute("SELECT * FROM Tutores")

        else:
            cursor.execute("SELECT * FROM Tutores WHERE Nome LIKE ?", ('%' + filtro + '%',))

        tutores_db = cursor.fetchall()
        self.table.setRowCount(0)
        for tutor in tutores_db:
            if filtro.lower() in tutor[1].lower():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(tutor[0])))
                self.table.setItem(row, 1, QTableWidgetItem(tutor[1]))
                self.table.setItem(row, 2, QTableWidgetItem(tutor[2]))
                self.table.setItem(row, 3, QTableWidgetItem(tutor[3]))
                self.table.setItem(row, 4, QTableWidgetItem(tutor[4]))

    def abrirFormularioTutor(self, tutor=None):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(f"{'Editar' if tutor else 'Adicionar'} Tutor")
        dialogo.setStyleSheet(f"background-color: #93cbd9;")
        layout = QVBoxLayout()
        formulario = QFormLayout()

        nome_input = QLineEdit(tutor['nome'] if tutor else '')
        telefone_input = QLineEdit(tutor['telefone'] if tutor else '')
        cpf_input = QLineEdit(tutor['cpf'] if tutor else '')

        # Funções de Formatação
        def formatar_telefone():
            texto = telefone_input.text()
            numeros = re.sub(r'\D', '', texto)[:11]
            tam = len(numeros)
            novo_texto = ""

            if tam >= 1:
                novo_texto += "(" + numeros[:2]

            if tam >= 3:
                novo_texto += ') ' + numeros[2:7]

            if tam >= 8:
                novo_texto += '-' + numeros[7:11]

            telefone_input.blockSignals(True)
            telefone_input.setText(novo_texto)
            telefone_input.blockSignals(False)

        def formatar_cpf(texto):
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

            cpf_input.blockSignals(True)
            cpf_input.setText(novo_texto)
            cpf_input.blockSignals(False)

        telefone_input.textChanged.connect(formatar_telefone)
        cpf_input.textChanged.connect(lambda texto: formatar_cpf(texto))
        
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

        if not dialogo.foto_path or not os.path.exists(dialogo.foto_path):
            caminho_padrao = os.path.join(FOTOS_TUTORES_DIR, "default-icon.png")
            dialogo.foto_path = caminho_padrao
            pixmap_padrao = QPixmap(caminho_padrao)
            foto_preview.setPixmap(pixmap_padrao)
            foto_label.setText("default-icon.png")

        botao_selecionar = QPushButton("Selecionar Foto")
        botao_selecionar.setStyleSheet(
            'background-color: #2f80ed; color: white; padding: 6px 12px; border-radius: 4px; '
            'border: none; font-size: 14px; font-weight: bold;'
            )
        botao_selecionar.clicked.connect(selecionar_foto)
        foto_layout.addWidget(botao_selecionar)
        foto_layout.addWidget(foto_label)
        
        formulario.addRow("Nome:", nome_input)
        formulario.addRow("Telefone:", telefone_input)
        formulario.addRow("CPF:", cpf_input)

        layout.addLayout(formulario)
        imagem_layout = QHBoxLayout()
        imagem_layout.addStretch()
        imagem_layout.addWidget(foto_preview)
        imagem_layout.addStretch()
        layout.addLayout(imagem_layout)
        layout.addLayout(foto_layout)
        
        botao_salvar = QPushButton("Salvar")
        botao_salvar.setStyleSheet(
            'background-color: #27ae60; color: white; padding: 6px 12px; border-radius: 4px; '
            'border: none; font-size: 14px; font-weight: bold;'
            )
        layout.addWidget(botao_salvar)
        dialogo.setLayout(layout)

        def salvar():
            nome = nome_input.text().strip()
            telefone = telefone_input.text().strip()
            cpf = cpf_input.text().strip()

            if not nome or not telefone or not cpf:
                QMessageBox.warning(dialogo, "Erro", "Todos os campos devem ser preenchidos.")
                return

            dialogo.resultado = {
                "nome": nome, 
                "telefone": telefone, 
                "cpf": cpf, 
                "foto_path": dialogo.foto_path
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

            cursor.execute("INSERT INTO Tutores (Nome, Telefone, CPF, Foto_Path) VALUES (?, ?, ?, ?)", (dados_tutor["nome"], dados_tutor["telefone"], dados_tutor["cpf"], 'NULL'))

            cursor.execute("""
                SELECT ID FROM Tutores WHERE CPF = ?
            """, (dados_tutor["cpf"],))

            id_tutor = cursor.fetchone()[0]
            novo_foto_path = dados_tutor["foto_path"]
            if dados_tutor["foto_path"]:
                ext = os.path.splitext(dados_tutor["foto_path"])[1]
                novo_nome_arquivo = f"tutor_{id_tutor}{ext}"
                novo_foto_path = os.path.join(FOTOS_TUTORES_DIR, novo_nome_arquivo)

                if not os.path.exists(novo_foto_path):
                    shutil.copy(dados_tutor["foto_path"], novo_foto_path)
            
            cursor.execute("""
                UPDATE Tutores
                SET Foto_Path = ?
                WHERE ID = ?
            """, (novo_foto_path, id_tutor))
            conexao.commit()

            QMessageBox.information(self, "Sucesso", "Tutor adicionado com sucesso!")
            self.atualizar_tabela()

    def editarTutor(self):
        linha = self.table.selectionModel().selectedRows()
        if not linha or len(linha) != 1:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos um tutor.")
            return

        linhaSelecionada = linha[0].row()

        tutor_atual = {
            'id': int(self.table.item(linhaSelecionada, 0).text()),
            'nome': self.table.item(linhaSelecionada, 1).text(),
            'telefone': self.table.item(linhaSelecionada, 2).text(),
            'cpf': self.table.item(linhaSelecionada, 3).text(),
            'foto_path': self.table.item(linhaSelecionada, 4).text()
        }
        
        dados_atualizados = self.abrirFormularioTutor(tutor_atual)
        if dados_atualizados:
            conexao = sqlite3.connect('dados.db')
            cursor = conexao.cursor()

            nova_foto_path = dados_atualizados['foto_path']

            if nova_foto_path != tutor_atual['foto_path']:
                if os.path.exists(tutor_atual['foto_path']) and tutor_atual['foto_path'] != 'NULL':
                    os.remove(tutor_atual['foto_path'])

                if not nova_foto_path.startswith(FOTOS_TUTORES_DIR):
                    ext = os.path.splitext(nova_foto_path)[1]
                    novo_nome_foto = f"tutor_{tutor_atual['id']}{ext}"
                    nova_foto_path = os.path.join(FOTOS_TUTORES_DIR, novo_nome_foto)

                    if not os.path.exists(nova_foto_path):
                        shutil.copy(dados_atualizados['foto_path'], nova_foto_path)

            cursor.execute("""
                UPDATE Tutores
                SET Nome = ?, Telefone = ?, CPF = ?, Foto_Path = ?
                WHERE ID = ?
            """, (
                dados_atualizados['nome'],
                dados_atualizados['telefone'],
                dados_atualizados['cpf'],
                nova_foto_path,
                tutor_atual['id']
            ))

            conexao.commit()

            QMessageBox.information(self, "Sucesso", "Tutor atualizado com sucesso!")
            self.atualizar_tabela()

    def deletarTutor(self):
        linhas = self.table.selectionModel().selectedRows()
        if not linhas or len(linhas) != 1:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos um tutor.")
            return

        resposta = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir os tutores selecionados?")

        if resposta == QMessageBox.StandardButton.Yes:
            for linha in sorted(linhas, reverse=True):
                tutor_id = int(self.table.item(linha.row(), 0).text())
                conexao = sqlite3.connect('dados.db')
                cursor = conexao.cursor()

                cursor.execute("""
                    SELECT ID FROM Pets WHERE Tutor_ID = ?
                """, (tutor_id,))

                ids_pets = [linha[0] for linha in cursor.fetchall()]

                for ids in ids_pets:
                    cursor.execute("""
                        DELETE FROM Pets WHERE ID = ?
                    """, (ids, ))

                    conexao.commit()

                cursor.execute("""
                    DELETE From Tutores
                    WHERE ID = ?
                """, (tutor_id,))

                conexao.commit()

                foto_path = self.table.item(linha.row(), 4).text()
                if foto_path and os.path.exists(foto_path):
                    os.remove(foto_path)

            QMessageBox.information(self, "Sucesso", "Tutor e seus Pets deletados com sucesso!")
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome do Pet", "Peso", "Raça", "Nome do Tutor"])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def adicionarPet(self):
        dados_pet = self.abrirFormulario()
        if dados_pet:
            cursor.execute("INSERT INTO Pets (Nome, Peso, Raca_ID, Tutor_ID) VALUES (?, ?, ?, ?)", (dados_pet['nome'], dados_pet['peso'], dados_pet['raca_id'], dados_pet['id_tutor']))

            conexao.commit()

            QMessageBox.information(self, "Sucesso", "Pet adicionado com sucesso!")
            self.atualizarTabela()

    def editarPet(self):
        linha = self.table.selectionModel().selectedRows()
        if not linha or len(linha) != 1:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos um pet.")
            return
        
        model = linha[0].model()
        index_coluna = model.index(linha[0].row(), 0)  # 2 é o número da coluna que você quer
        pet_id = index_coluna.data()
        
        cursor.execute("SELECT Nome, Peso, Raca_ID, Tutor_ID FROM Pets WHERE ID = ?", (pet_id,))

        pet_atual = cursor.fetchall()[0]

        dados_atualizado = self.abrirFormulario(pet_atual)
        if dados_atualizado:
            cursor.execute("UPDATE Pets SET Nome = ?, Peso = ?, Raca_ID = ?, Tutor_ID = ? WHERE ID = ?", (dados_atualizado['nome'], dados_atualizado['peso'], dados_atualizado['raca_id'], dados_atualizado['id_tutor'], pet_id))
            conexao.commit()
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

                cursor.execute("DELETE FROM Pets WHERE ID = ?", (pet_id,))
                conexao.commit()

            QMessageBox.information(self, "Sucesso", "Pet deletado com sucesso!")
            self.atualizarTabela()

    def atualizarTabela(self):
        filtro = self.petInput.text().lower()
        # conecta no banco de dados e busca pets com o filtro

        cursor.execute("SELECT * FROM Pets")
        self.pets_db = cursor.fetchall()

        self.table.setRowCount(0)
        for pet in self.pets_db:
            cursor.execute("SELECT Nome FROM Tutores WHERE ID = ?", (pet[4],))
            tutor_nome = cursor.fetchall()[0][0]
            if filtro in pet[1].lower() or filtro in tutor_nome.lower():
                linha = self.table.rowCount()
                self.table.insertRow(linha)
                
                cursor.execute("SELECT Nome FROM Racas WHERE ID = ?", (pet[3],))
                raca_nome = cursor.fetchall()[0][0]

                self.table.setItem(linha, 0, QTableWidgetItem(str(pet[0])))
                self.table.setItem(linha, 1, QTableWidgetItem(pet[1]))
                self.table.setItem(linha, 2, QTableWidgetItem(pet[2]))
                self.table.setItem(linha, 3, QTableWidgetItem(raca_nome))
                self.table.setItem(linha, 4, QTableWidgetItem(tutor_nome))

    def abrirFormulario(self, pet=None):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(f"{'Editar' if pet else 'Adicionar'} Pet")
        dialogo.setStyleSheet(f"background-color: #93cbd9;")
        layout = QVBoxLayout()

        conexao = sqlite3.connect('dados.db')
        cursor = conexao.cursor()

        nome_input = QLineEdit()

        peso_input = QLineEdit()
        
        def formatar_peso(texto):
            texto_limpo = re.sub(r'[^0-9.]', '', texto)

            partes = texto_limpo.split('.')

            if len(partes) > 1:
                inteiro = partes[0]
                decimal = ''.join(partes[1:])[:2]  
                texto_limpo = inteiro + '.' + decimal

            else:
                texto_limpo = partes[0]

            peso_input.blockSignals(True)
            peso_input.setText(texto_limpo)
            peso_input.blockSignals(False)
            
        peso_input.textChanged.connect(formatar_peso)       

        raca_input = QComboBox()

        cursor.execute("SELECT Nome, ID FROM Racas")
        racas = cursor.fetchall()

        for raca_nome, raca_id in racas:
            raca_input.addItem(raca_nome, userData=raca_id)

        tutor_input = QComboBox()
            
        cursor.execute("SELECT Nome, ID FROM Tutores")
        tutores = cursor.fetchall()

        for tutor_nome, tutor_id in tutores:
            tutor_input.addItem(tutor_nome, userData=tutor_id)
        
        if pet:
            nome_input.setText(pet[0])
            peso_input.setText(str(pet[1]))
            raca_input.setCurrentIndex(raca_input.findData(pet[2]))
            tutor_input.setCurrentIndex(tutor_input.findData(pet[3]))



        formulario = QFormLayout()
        formulario.addRow("Nome:", nome_input)
        formulario.addRow("Peso:", peso_input)
        formulario.addRow("Dono:", tutor_input)
        formulario.addRow("Raça:", raca_input)

        botao_salvar = QPushButton("Salvar")
        botao_salvar.setStyleSheet(
            'background-color: #27ae60; color: white; padding: 6px 12px; border-radius: 4px; '
            'border: none; font-size: 14px; font-weight: bold;'
            )
        layout.addLayout(formulario)
        layout.addWidget(botao_salvar)
        dialogo.setLayout(layout)

        def salvar():
            nome = nome_input.text().strip()
            peso = peso_input.text().strip()
            raca_id = raca_input.currentData()
            tutor_id = tutor_input.currentData()

            if not nome:
                QMessageBox.warning(dialogo, "Erro", "Nome não pode estar vazio.")
                return
            
            dialogo.accept()
            dialogo.resultado = {
                "nome": nome, 
                "peso": peso, 
                "raca_id": raca_id,
                "id_tutor": tutor_id 
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


class TelaVeterinario(QWidget):
    def __init__(self, tela_inicial, perfil_logado):
        super().__init__()
        uic.loadUi("tela_veterinario.ui", self)

        self.tela_inicial = tela_inicial
        self.perfil_logado = perfil_logado 

        self.configurar_tela()

    def configurar_tela(self):
        self.tabelaConsultasHoje.setColumnCount(5)
        self.tabelaConsultasHoje.setHorizontalHeaderLabels(["ID", "Horário", "Pet", "Tutor", "Status"])
        self.tabelaConsultasHoje.setColumnHidden(0, True)
        self.tabelaConsultasHoje.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabelaConsultasHoje.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabelaConsultasHoje.setColumnWidth(2, 180)
        self.tabelaConsultasHoje.setColumnWidth(3, 180)

        self.realizarDiagnosticoBTN.clicked.connect(self.realizar_diagnostico)
        self.sairBTN.clicked.connect(self.sair)
        
        self.tabelaConsultasHoje.itemSelectionChanged.connect(self.atualizar_status_botao_diagnostico)

        self.atualizar_status_botao_diagnostico()
        
        self.carregar_consultas_de_hoje()

    def carregar_consultas_de_hoje(self):
        self.tabelaConsultasHoje.setRowCount(0)
        hoje_str = QDate.currentDate().toString("dd/MM/yyyy")
        
        conexao = sqlite3.connect('dados.db')
        cursor = conexao.cursor()
        query = """
            SELECT c.ID, c.Data_Horario, p.Nome AS PetNome, t.Nome AS TutorNome, c.Relatorio_ID
            FROM Consultas c
            JOIN Pets p ON c.Pet_ID = p.ID
            JOIN Tutores t ON p.Tutor_ID = t.ID
            WHERE c.Perfil_Medico_ID = ? AND c.Data_Horario LIKE ?
            ORDER BY c.Data_Horario
        """
        cursor.execute(query, (self.perfil_logado.id, f'{hoje_str}%'))
        consultas = cursor.fetchall()
        conexao.close()
        
        for consulta in consultas:
            consulta_id, data_hora, pet_nome, tutor_nome, relatorio_id = consulta
            
            hora = datetime.strptime(data_hora, '%d/%m/%Y %H:%M').strftime('%H:%M')
            status = "Concluído" if relatorio_id else "Pendente"
            
            row = self.tabelaConsultasHoje.rowCount()
            self.tabelaConsultasHoje.insertRow(row)
            self.tabelaConsultasHoje.setItem(row, 0, QTableWidgetItem(str(consulta_id)))
            self.tabelaConsultasHoje.setItem(row, 1, QTableWidgetItem(hora))
            self.tabelaConsultasHoje.setItem(row, 2, QTableWidgetItem(pet_nome))
            self.tabelaConsultasHoje.setItem(row, 3, QTableWidgetItem(tutor_nome))
            self.tabelaConsultasHoje.setItem(row, 4, QTableWidgetItem(status))

    def atualizar_status_botao_diagnostico(self):
        itens_selecionados = self.tabelaConsultasHoje.selectedItems()
        
        if not itens_selecionados:
            self.realizarDiagnosticoBTN.setEnabled(False)
            return

        linha_selecionada = self.tabelaConsultasHoje.currentRow()
        status = self.tabelaConsultasHoje.item(linha_selecionada, 4).text()
        
        self.realizarDiagnosticoBTN.setEnabled(status == "Pendente")

    def realizar_diagnostico(self):
        linha_selecionada = self.tabelaConsultasHoje.currentRow()
        if linha_selecionada < 0: 
            return

        consulta_id = int(self.tabelaConsultasHoje.item(linha_selecionada, 0).text())

        diagnostico, ok = QInputDialog.getMultiLineText(self, "Realizar Diagnóstico", "Digite a descrição e o diagnóstico do paciente:")
        
        if ok and diagnostico.strip():
            conexao = sqlite3.connect('dados.db')
            cursor = conexao.cursor()
            cursor.execute("INSERT INTO Relatorios (Descricao, Diagnostico) VALUES (?, ?)", (diagnostico, diagnostico))
            relatorio_id = cursor.lastrowid
            
            cursor.execute("UPDATE Consultas SET Relatorio_ID = ? WHERE ID = ?", (relatorio_id, consulta_id))
            
            conexao.commit()
            conexao.close()
            
            QMessageBox.information(self, "Sucesso", "Diagnóstico salvo com sucesso!")
            self.carregar_consultas_de_hoje()

    def sair(self):
        self.tela_inicial.show()
        self.close()

janela = TelaInicial()
janela.show()
app.exec()