class Perfil():
    def __init__(self, login, senha], cargo_id):
        self.login = login
        self.__senha_hash = gerar_senha_hash(senha)

    def gerar_senha_hash(self, senha):