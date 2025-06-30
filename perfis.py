import bcrypt
import sqlite3

class Perfil():
    def __init__(self, nome, senha, cargo_id, data_nasc, cpf, email):
        self.nome = nome
        self.data_nasc = data_nasc
        self.cpf = cpf
        self.email = email
        self.__senha_hash = self.gerar_senha_hash(senha)
        self.cargo_id = cargo_id

    def get_senha_hash(self):
        return self.__senha_hash

    def gerar_senha_hash(self, senha_plana):
        senha_bytes = senha_plana.encode('utf-8')
        salt = bcrypt.gensalt()
        hash_senha = bcrypt.hashpw(senha_bytes, salt)
        return hash_senha
        
    def verificar_senha(self, senha_recebida):
        senha_bytes = senha_recebida.encode('utf-8')
        return bcrypt.checkpw(senha_bytes, self.get_senha_hash())

    def salvar_dados(self):
        conexao = sqlite3.connect('dados.db')
        cursor = conexao.cursor()

        cursor.execute(f"INSERT INTO Perfis (Nome, Data_Nasc, CPF, Email, Senha_Hash, Cargo_ID) VALUES (?, ?, ?, ?, ?, ?)", (self. nome, self.data_nasc, self.cpf, self.email, self.get_senha_hash(), self.cargo_id))

        conexao.commit()

