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
from PyQt6.QtCore import QDate


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
                self.login_input.setStyleSheet("border-radius: 4px; border: 2px solid #e74c3c;")
                self.labelWarning1.setText("")
                self.senha_input.setStyleSheet("border-radius: 4px; border: 2px solid #e74c3c;")
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

        self.login_input.setStyleSheet("border-radius: 4px; border: none;")
        self.senha_input.setStyleSheet("border-radius: 4px; border: none;")

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
                widget.setStyleSheet("border-radius: 4px; border: 2px solid #e74c3c;")
                warning.setText("Preencha o campo")
                valido = False

            elif funcao_validacao and not funcao_validacao(valor):
                widget.setStyleSheet("border-radius: 4px;'border: 2px solid #e74c3c;")

                if campo == 'cpf':
                    warning.setText("CPF inválido")
                elif campo == 'telefone':
                    warning.setText("Telefone inválido")
                elif campo == 'email':
                    warning.setText("Formato de e-mail inválido")

                valido = False
            else:
                widget.setStyleSheet("border-radius: 4px; border: none;")
                warning.setText("")

        if not dados["recepcionista"] and not dados["veterinario"]:
            self.labelWarning7.setText("Escolha um cargo")
            valido = False
        else:
            self.labelWarning7.setText("")

        resultado_validacao, mensagem_validacao = self.validar_senha(dados["senha"])
        if not resultado_validacao:
            self.senha_input.setStyleSheet("border-radius: 4px; border: 2px solid #e74c3c;")
            self.confirmar_senha_input.setStyleSheet("border-radius: 4px; border: 2px solid #e74c3c;")
            self.labelWarning5.setText(mensagem_validacao)
            self.labelWarning6.setText("")
            valido = False

        elif dados["senha"] != dados["confirmar_senha"]:
            self.senha_input.setStyleSheet("border-radius: 4px; border: 2px solid #e74c3c;")
            self.confirmar_senha_input.setStyleSheet("border-radius: 4px; border: 2px solid #e74c3c;")
            self.labelWarning5.setText("As senhas não coincidem")
            self.labelWarning6.setText("As senhas não coincidem")
            valido = False

        else:
            if dados["senha"]:
                self.senha_input.setStyleSheet("border-radius: 4px; border: none;")
                self.confirmar_senha_input.setStyleSheet("border-radius: 4px; border: none;")
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

        self.addConsultaBTN.clicked.connect(self.adicionarConsulta)

        self.petsBTN.clicked.connect(self.openTelaPet)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)
        self.vetBTN.clicked.connect(self.openTelaVeterinario)
        self.sairBTN.clicked.connect(self.logout)

        self.calendarWidget.activated.connect(self.consultasDataSelecionada)

        self.atualizar_cores_calendario()

    def criar_formato(self, cor):
        formato = QTextCharFormat()
        formato.setBackground(cor)
        formato.setFontWeight(QFont.Weight.Bold)
        return formato

    def atualizar_cores_calendario(self):
        formato_padrao = QTextCharFormat()
        for data_marcada in self.datas_marcadas:
            self.calendarWidget.setDateTextFormat(data_marcada, formato_padrao)
        self.datas_marcadas.clear()

        formatos = {
            1: self.criar_formato(QColor("#3498db")),
            2: self.criar_formato(QColor("#2ecc71")),
            3: self.criar_formato(QColor("#f39c12")),
            4: self.criar_formato(QColor("#e74c3c"))
        }

    
        cursor.execute("SELECT Data, COUNT(ID) FROM Consultas GROUP BY Data")
        contagem_por_data = cursor.fetchall()

        for data_str, contagem in contagem_por_data:
            data = QDate.fromString(data_str, "dd/MM/yyyy")

            self.calendarWidget.setDateTextFormat(data, formatos.get(min(contagem, 4)))
            self.datas_marcadas.add(data) 
                    
    def consultasDataSelecionada(self, data):
        dialogo = TelaConsultasDataSelecionada(data, self)

        dialogo.exec()

    def abrirFormularioConsulta(self, data=None, consulta=None):
        dialogo = TelaCrudConsulta(self)
        dialogo.setWindowTitle(f"{'Editar' if consulta else 'Adicionar'} Consulta")

        cursor.execute("SELECT Nome, ID FROM Pets")
        pets = cursor.fetchall()
        dialogo.pet_input.addItem("Selecione um pet")
        for pet_nome, pet_id in pets:
            dialogo.pet_input.addItem(pet_nome, userData=pet_id)
        
        cursor.execute("SELECT Nome, ID FROM Perfis WHERE Cargo_ID = ?", (2,))
        veterinarios = cursor.fetchall()
        dialogo.veterinario_input.addItem("Selecione um veterinário", userData=None)
        for vet_nome, vet_id in veterinarios:
            dialogo.veterinario_input.addItem(vet_nome, userData=vet_id)

        data_salvar = None

        if consulta:
            dialogo.pet_input.setCurrentIndex(dialogo.pet_input.findData(consulta[0]))
            dialogo.veterinario_input.setCurrentIndex(dialogo.veterinario_input.findData(consulta[1]))
            dialogo.data_label.setText(f"Data da Consulta - {consulta[3]}")
            data_salvar = consulta[3]
        else:
            dialogo.data_label.setText(f"Nova data da Consulta - {data.toString('dd/MM/yyyy')}")
            data_salvar = data.toString("dd/MM/yyyy")

        def salvar():
            pet_id = dialogo.pet_input.currentData()
            veterinario_id = dialogo.veterinario_input.currentData()
            horario = dialogo.horario_input.time().toString("HH:mm")

            if not pet_id or not veterinario_id:
                QMessageBox.warning(dialogo, "Erro", "Por favor selecione um pet e um veterinário.")
                return

            dialogo.resultado = {
                "data": data_salvar,
                "pet_id": pet_id,
                "veterinario_id": veterinario_id,
                "horario": horario
            }
            dialogo.accept()

        dialogo.botao_salvar.clicked.connect(salvar)

        if dialogo.exec():
            return dialogo.resultado
        return None

    def adicionarConsulta(self):
        data = self.calendarWidget.selectedDate()
        dados_consulta = self.abrirFormularioConsulta(data = data)
        cursor.execute("INSERT INTO Consultas (Pet_ID, Perfil_Medico_ID, Data, Horario) VALUES (?, ?, ?, ?)", (dados_consulta['pet_id'], dados_consulta['veterinario_id'], dados_consulta['data'], dados_consulta['horario']))
        conexao.commit()
        QMessageBox.information(self, "Sucesso", "Consulta adicionada com sucesso!")
        self.atualizar_cores_calendario()

    def openTelaPet(self):
        self.tela_pet = TelaPet(self.tela_inicial)
        self.tela_pet.show()
        self.hide()

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor(self.tela_inicial)
        self.tela_tutor.show()
        self.hide()

    def openTelaVeterinario(self):
        self.tela_consulta = TelaVeterinarioRecepcionista(self.tela_inicial)
        self.tela_consulta.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


class TelaConsultasDataSelecionada(QDialog):
    def __init__(self, data_selecionada=None, parent=None):
        super().__init__(parent)
        uic.loadUi("tela_todas_consultas.ui", self)

        self.setWindowTitle(f"Tela Recepcionista - Consultas do dia {data_selecionada.toString('dd/MM/yyyy')}")

        self.data_selecionada = data_selecionada

        self.editConsultaBTN.clicked.connect(self.editarConsulta)
        self.delConsultaBTN.clicked.connect(self.deletarConsulta)
        
        self.configurar_tabela()
        self.carregar_consultas()

    def configurar_tabela(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Pet', 'Tutor', 'Veterinário', 'Horário'])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def carregar_consultas(self):
        self.table.setRowCount(0)
        data_para_busca = self.data_selecionada.toString('dd/MM/yyyy')

        with sqlite3.connect('dados.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT ID, Pet_ID, Perfil_Medico_ID, Horario FROM Consultas WHERE Data = ? ORDER BY Horario", (data_para_busca,))
            consultas_base = cursor.fetchall()

            if not consultas_base:
                QMessageBox.information(self, "Informação", "Nenhuma consulta encontrada para esta data.")
                return

            for consulta in consultas_base:
                id_consulta, pet_id, medico_id, horario = consulta

                cursor.execute("SELECT Nome, Tutor_ID FROM Pets WHERE ID = ?", (pet_id,))
                resultado_pet = cursor.fetchone()
                if resultado_pet:
                    nome_pet, tutor_id = resultado_pet
                else:
                    nome_pet, tutor_id = "Pet Excluído", None

                nome_tutor = "Tutor Excluído"
                if tutor_id:
                    cursor.execute("SELECT Nome FROM Tutores WHERE ID = ?", (tutor_id,))
                    resultado_tutor = cursor.fetchone()
                    if resultado_tutor:
                        nome_tutor = resultado_tutor[0]

                cursor.execute("SELECT Nome FROM Perfis WHERE ID = ?", (medico_id,))
                resultado_vet = cursor.fetchone()
                if resultado_vet:
                    nome_vet = resultado_vet[0]
                else:
                    nome_vet = "Veterinário Excluído"

                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0, QTableWidgetItem(str(id_consulta)))
                self.table.setItem(row, 1, QTableWidgetItem(nome_pet))
                self.table.setItem(row, 2, QTableWidgetItem(nome_tutor))
                self.table.setItem(row, 3, QTableWidgetItem(nome_vet))
                self.table.setItem(row, 4, QTableWidgetItem(horario))

    def editarConsulta(self):
        linha = self.table.selectionModel().selectedRows()
        if not linha or len(linha) != 1:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos uma consulta.")
            return
        
        model = linha[0].model()
        index_coluna = model.index(linha[0].row(), 0)  
        consulta_id = index_coluna.data()
        
        cursor.execute("SELECT Pet_ID, Perfil_Medico_ID, Relatorio_ID, Data, Horario FROM Consultas WHERE ID = ?", (consulta_id,))

        consulta_atual = cursor.fetchall()[0]

        dados_atualizado = self.parent().abrirFormularioConsulta(consulta=consulta_atual)
        if dados_atualizado:
            cursor.execute("UPDATE Consultas SET Pet_ID = ?, Perfil_Medico_ID = ?, Relatorio_ID = ?, Data = ?, Horario = ? WHERE ID = ?", (dados_atualizado['pet_id'], dados_atualizado['veterinario_id'], None, dados_atualizado['data'], dados_atualizado['horario'], consulta_id))
            conexao.commit()
            QMessageBox.information(self, "Sucesso", "Consulta atualizada com sucesso!")
            self.carregar_consultas()

    def deletarConsulta(self):
        linhas = self.table.selectionModel().selectedRows()
        if not linhas:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione pelo menos uma consulta.")
            return
        resposta = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir a consulta selecionada?")
        if resposta == QMessageBox.StandardButton.Yes:
            for linha in sorted(linhas, reverse=True):
                consulta_id = int(self.table.item(linha.row(), 0).text())

                cursor.execute("DELETE FROM Consultas WHERE ID = ?", (consulta_id,))
                conexao.commit()

            QMessageBox.information(self, "Sucesso", "Consulta deletada com sucesso!")
            self.carregar_consultas()


class TelaCrudConsulta(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("tela_crud_consulta.ui", self)


class TelaTutor(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_recepcionista_Tutor.ui", self)
        
        self.tela_inicial = tela_inicial

        self.petsBTN.clicked.connect(self.openTelaPet)
        self.consultasBTN.clicked.connect(self.openTelaConsulta)
        self.vetBTN.clicked.connect(self.openTelaVeterinario)
        self.sairBTN.clicked.connect(self.logout)

        self.addTutorBTN.clicked.connect(self.adicionarTutor)
        self.editTutorBTN.clicked.connect(self.editarTutor)
        self.delTutorBTN.clicked.connect(self.deletarTutor)
        self.tutorInput.textChanged.connect(self.atualizar_tabela)

        self.table.cellDoubleClicked.connect(self.abrirPerfil)

        self.configurar_tabela()
        self.atualizar_tabela()

    def configurar_tabela(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Nome', 'Telefone', 'CPF', 'Foto Path'])
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(4, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def abrirPerfil(self, linha, coluna):
        valores = []
        for col in range(self.table.columnCount()):
            item = self.table.item(linha, col)
            valores.append(item.text() if item else "")
        
        self.tela_perfil = TelaPerfilTutor(valores)
        self.tela_perfil.show()

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
        dialogo = TelaCrudTutor(self)
        dialogo.setWindowTitle(f"{'Editar' if tutor else 'Adicionar'} Tutor")

        if tutor:
            dialogo.nome_input.setText(tutor['nome'])
            dialogo.telefone_input.setText(tutor['telefone'])
            dialogo.cpf_input.setText(tutor['cpf'])

        def formatar_nome():
            texto = dialogo.nome_input.text()
            novo_texto = re.sub(r'[^a-zA-Z\s]', '', texto)
            dialogo.nome_input.blockSignals(True)
            dialogo.nome_input.setText(novo_texto)
            dialogo.nome_input.blockSignals(False)

        def formatar_telefone():
            texto = dialogo.telefone_input.text()
            numeros = re.sub(r'\D', '', texto)[:11]
            tam = len(numeros)
            novo_texto = ""

            if tam >= 1: 
                novo_texto += "(" + numeros[:2]

            if tam >= 3:
                novo_texto += ') ' + numeros[2:7]

            if tam >= 8:
                novo_texto += '-' + numeros[7:11]

            dialogo.telefone_input.blockSignals(True)
            dialogo.telefone_input.setText(novo_texto)
            dialogo.telefone_input.blockSignals(False)

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

            dialogo.cpf_input.blockSignals(True)
            dialogo.cpf_input.setText(novo_texto)
            dialogo.cpf_input.blockSignals(False)

        dialogo.nome_input.textChanged.connect(formatar_nome)
        dialogo.telefone_input.textChanged.connect(formatar_telefone)
        dialogo.cpf_input.textChanged.connect(formatar_cpf)

        dialogo.foto_path = tutor['foto_path'] if tutor else ''
        if dialogo.foto_path and os.path.exists(dialogo.foto_path):
            dialogo.foto_preview.setPixmap(QPixmap(dialogo.foto_path))
            dialogo.foto_label.setText(os.path.basename(dialogo.foto_path))
        else:
            caminho_padrao = os.path.join(FOTOS_TUTORES_DIR, "default-icon.png")
            if os.path.exists(caminho_padrao):
                dialogo.foto_path = caminho_padrao
                dialogo.foto_preview.setPixmap(QPixmap(caminho_padrao))
                dialogo.foto_label.setText("default-icon.png")

        def selecionar_foto():
            fname, _ = QFileDialog.getOpenFileName(self, 'Selecionar Foto', '', 'Imagens (*.png *.jpg *.jpeg)')
            if fname:
                dialogo.foto_path = fname
                dialogo.foto_preview.setPixmap(QPixmap(fname))
                dialogo.foto_label.setText(os.path.basename(fname))

        dialogo.botao_selecionar.clicked.connect(selecionar_foto)
        
        def salvar():
            nome = dialogo.nome_input.text().strip()
            telefone = dialogo.telefone_input.text().strip()
            cpf = dialogo.cpf_input.text().strip()

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

        dialogo.botao_salvar.clicked.connect(salvar)

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

    def openTelaVeterinario(self):
        self.tela_consulta = TelaVeterinarioRecepcionista(self.tela_inicial)
        self.tela_consulta.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


class TelaCrudTutor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("tela_crud_tutor.ui", self)


class TelaPerfilTutor(QWidget):
    def __init__(self, dados):
        super().__init__()
        uic.loadUi("tela_perfil_tutor.ui", self)

        self.labelID.setText(dados[0])
        self.labelNome.setText(dados[1])
        self.labelTelefone.setText(dados[2])
        self.labelCPF.setText(dados[3])
        self.labelImagem.setPixmap(QPixmap(dados[4]))

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Pet", "Peso (kg)", "Raça"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        
        cursor.execute("SELECT ID, Nome, Peso, Raca_ID FROM Pets WHERE Tutor_ID = ?", (dados[0],))
        pets_db = cursor.fetchall()

        self.table.setRowCount(0)

        for pet in pets_db:
            cursor.execute("SELECT Nome FROM Racas WHERE ID = ?", (pet[3],))
            raca = cursor.fetchall()[0][0]
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(pet[0])))
            self.table.setItem(row, 1, QTableWidgetItem(pet[1]))
            self.table.setItem(row, 2, QTableWidgetItem(pet[2]))
            self.table.setItem(row, 3, QTableWidgetItem(raca))



class TelaPet(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_recepcionista_pet.ui", self)
        
        self.tela_inicial = tela_inicial

        self.addPetBTN.clicked.connect(self.adicionarPet)
        self.editPetBTN.clicked.connect(self.editarPet)
        self.delPetBTN.clicked.connect(self.deletarPet)

        self.consultasBTN.clicked.connect(self.openTelaConsulta)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)
        self.vetBTN.clicked.connect(self.openTelaVeterinario)
        self.sairBTN.clicked.connect(self.logout)

        self.table.cellDoubleClicked.connect(self.abrirPerfil)

        self.petInput.textChanged.connect(self.atualizarTabela)

        self.configurarTabela()
        self.atualizarTabela()

    def configurarTabela(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Pet", "Peso (kg)", "Raça", "Tutor"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def atualizarTabela(self):
        filtro = self.petInput.text().lower()

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

    def abrirPerfil(self, linha, coluna):
        valores = []
        for col in range(self.table.columnCount()):
            item = self.table.item(linha, col)
            valores.append(item.text() if item else "")
        
        self.tela_perfil = TelaPerfilPet(valores)
        self.tela_perfil.show()

    def abrirFormulario(self, pet=None):
        dialogo = TelaCrudPet(self)
        dialogo.setWindowTitle(f"{'Editar' if pet else 'Adicionar'} Pet")

        conexao = sqlite3.connect('dados.db')
        cursor = conexao.cursor()
        
        def formatar_peso(texto):
            texto_limpo = re.sub(r'[^0-9.]', '', texto)

            partes = texto_limpo.split('.')

            if len(partes) > 1:
                inteiro = partes[0]
                decimal = ''.join(partes[1:])[:2]  
                texto_limpo = inteiro + '.' + decimal

            else:
                texto_limpo = partes[0]

            dialogo.peso_input.blockSignals(True)
            dialogo.peso_input.setText(texto_limpo)
            dialogo.peso_input.blockSignals(False)
            
        dialogo.peso_input.textChanged.connect(formatar_peso)       

        cursor.execute("SELECT Nome, ID FROM Racas")
        racas = cursor.fetchall()

        for raca_nome, raca_id in racas:
            dialogo.raca_input.addItem(raca_nome, userData=raca_id)
            
        cursor.execute("SELECT Nome, ID FROM Tutores")
        tutores = cursor.fetchall()

        for tutor_nome, tutor_id in tutores:
            dialogo.tutor_input.addItem(tutor_nome, userData=tutor_id)
        
        if pet:
            dialogo.nome_input.setText(pet[0])
            dialogo.peso_input.setText(str(pet[1]))
            dialogo.raca_input.setCurrentIndex(dialogo.raca_input.findData(pet[2]))
            dialogo.tutor_input.setCurrentIndex(dialogo.tutor_input.findData(pet[3]))

        def salvar():
            nome = dialogo.nome_input.text().strip()
            peso = dialogo.peso_input.text().strip()
            raca_id = dialogo.raca_input.currentData()
            tutor_id = dialogo.tutor_input.currentData()

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

        dialogo.botao_salvar.clicked.connect(salvar)
        if dialogo.exec():
            return dialogo.resultado
        return None

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
        index_coluna = model.index(linha[0].row(), 0)  
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
        resposta = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir o pet selecionado?")
        if resposta == QMessageBox.StandardButton.Yes:
            for linha in sorted(linhas, reverse=True):
                pet_id = int(self.table.item(linha.row(), 0).text())

                cursor.execute("DELETE FROM Pets WHERE ID = ?", (pet_id,))
                conexao.commit()

            QMessageBox.information(self, "Sucesso", "Pet deletado com sucesso!")
            self.atualizarTabela()

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor(self.tela_inicial)
        self.tela_tutor.show()
        self.hide()
    
    def openTelaConsulta(self):
        self.tela_consulta = TelaConsulta(self.tela_inicial)
        self.tela_consulta.show()
        self.hide()

    def openTelaVeterinario(self):
        self.tela_consulta = TelaVeterinarioRecepcionista(self.tela_inicial)
        self.tela_consulta.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


class TelaCrudPet(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("tela_crud_pet.ui", self)


class TelaPerfilPet(QWidget):
    def __init__(self, dados):
        super().__init__()
        uic.loadUi("tela_perfil_pet.ui", self)

        self.labelID.setText(dados[0])
        self.labelNome.setText(dados[1])
        self.labelPeso.setText(dados[2])
        self.labelRaca.setText(dados[3])
        self.labelTutor.setText(dados[4])

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Veterinário", "Data", "Horário"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        cursor.execute("SELECT Perfil_Medico_ID, Data, Horario FROM Consultas WHERE Pet_ID = ?", (dados[0],))
        consultas_db = cursor.fetchall()

        self.table.setRowCount(0)

        for consulta in consultas_db:
            cursor.execute("SELECT Nome FROM Perfis WHERE ID = ?", (consulta[0],))
            med_vet = cursor.fetchall()[0][0]
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(med_vet))
            self.table.setItem(row, 1, QTableWidgetItem(consulta[1]))
            self.table.setItem(row, 2, QTableWidgetItem(consulta[2]))


class TelaVeterinarioRecepcionista(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_recepcionista_veterinario.ui", self)
        
        self.tela_inicial = tela_inicial

        self.petsBTN.clicked.connect(self.openTelaPet)
        self.consultasBTN.clicked.connect(self.openTelaConsulta)
        self.tutoresBTN.clicked.connect(self.openTelaTutor)
        self.sairBTN.clicked.connect(self.logout)

        self.table.cellDoubleClicked.connect(self.abrirPerfil)

        self.vetInput.textChanged.connect(self.atualizar_tabela)

        self.configurar_tabela()
        self.atualizar_tabela()

    def configurar_tabela(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Nome', 'CPF', 'Email'])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def atualizar_tabela(self):
        filtro = self.vetInput.text().strip()

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

    def abrirPerfil(self, linha, coluna):
        valores = []
        for col in range(self.table.columnCount()):
            item = self.table.item(linha, col)
            valores.append(item.text() if item else "")
        
        self.tela_perfil = TelaPerfilVeterinario(valores)
        self.tela_perfil.show()

    def openTelaConsulta(self):
        self.tela_consulta = TelaConsulta(self.tela_inicial)
        self.tela_consulta.show()
        self.hide()

    def openTelaTutor(self):
        self.tela_tutor = TelaTutor(self.tela_inicial)
        self.tela_tutor.show()
        self.hide()

    def openTelaPet(self):
        self.tela_pet = TelaPet(self.tela_inicial)
        self.tela_pet.show()
        self.hide()

    def logout(self):
        self.tela_inicial.show()
        self.close()


class TelaPerfilVeterinario(QWidget):
    def __init__(self, dados):
        super().__init__()
        uic.loadUi("tela_perfil_veterinario.ui", self)

        self.setWindowTitle(f'Dados do Veterinário - {dados[1]}')

        self.labelID.setText(dados[0])
        self.labelNome.setText(dados[1])
        self.labelCPF.setText(dados[2])
        self.labelEmail.setText(dados[3])

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Pet", "Tutor", "Data", "Horário"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # conectar banco de dados e dar todas as consultas de um veterinário


class TelaVeterinario(QWidget):
    def __init__(self, tela_inicial):
        super().__init__()
        uic.loadUi("tela_veterinario.ui", self)

        self.tela_inicial = tela_inicial

        self.diagnosticoBTN.clicked.connect(self.realizarDiagnostico)
        self.sairBTN.clicked.connect(self.logout)

        self.tutorInput.textChanged.connect(self.atualizarTabela)

        self.configurarTabela()
        self.atualizarTabela()

    def configurarTabela(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Pet", "Tutor", "Data", "Horário"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def atualizarTabela(self):
        filtro = self.tutorInput.text().lower()

        cursor.execute("SELECT * FROM Consultas")
        self.consultas_db = cursor.fetchall()

        self.table.setRowCount(0)
        for consulta in self.consultas_db:
            pass
            # cursor.execute("SELECT Nome FROM Tutores WHERE ID = ?", (consulta[4],))
            # tutor_nome = cursor.fetchall()[0][0]
            # if filtro in consulta[1].lower() or filtro in tutor_nome.lower():
            #     linha = self.table.rowCount()
            #     self.table.insertRow(linha)
                
            #     cursor.execute("SELECT Nome FROM Racas WHERE ID = ?", (consulta[3],))
            #     raca_nome = cursor.fetchall()[0][0]

            #     self.table.setItem(linha, 0, QTableWidgetItem(str(consulta[0])))
            #     self.table.setItem(linha, 1, QTableWidgetItem(consulta[1]))
            #     self.table.setItem(linha, 2, QTableWidgetItem(consulta[2]))
            #     self.table.setItem(linha, 3, QTableWidgetItem(raca_nome))
            #     self.table.setItem(linha, 4, QTableWidgetItem(tutor_nome))

    def realizarDiagnostico(self):
        pass

    def logout(self):
        self.tela_inicial.show()
        self.close()

janela = TelaInicial()
janela.show()
app.exec()