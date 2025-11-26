import bcrypt
from .gerencia_BD import GerenciadorMongoDB


class GerenciaUsuario:
    def __init__(self, db_gerencia: GerenciadorMongoDB):
        self.db_gerencia = db_gerencia
        self.colecao_nomes = "usuarios"

    def cadastrar_usuario(self, nome_usuario, senha, empresa, email):
        if self.db_gerencia.find_one(
            self.colecao_nomes, {"nome_usuario": nome_usuario}
        ):
            print("Usuário já existe. Escolha outro nome de usuário.")
            return False

        senha_criptografada = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
        dados_usuario = {
            "nome_usuario": nome_usuario,
            "senha": senha_criptografada.decode("utf-8"),
            "empresa": empresa,
            "email": email
        }
        resultado = self.db_gerencia.insert_one(self.colecao_nomes, dados_usuario)
        if resultado and resultado.inserted_id:
            print(f"Usuário {nome_usuario} cadastrado com sucesso!")
            return True
        return False

    def verificar_usuario(self, nome_usuario, senha):
        user = self.db_gerencia.find_one(
            self.colecao_nomes, {"nome_usuario": nome_usuario}
        )
        if user:
            if bcrypt.checkpw(senha.encode("utf-8"), user["senha"].encode("utf-8")):
                print("Login bem-sucedido!")
                return True
            else:
                print("Senha incorreta.")
                return False
        else:
            print("Usuário não encontrado.")
            return False

    def deletar_usuario(self, nome_usuario):
        resultado = self.db_gerencia.delete_one(
            self.colecao_nomes, {"nome_usuario": nome_usuario}
        )
        if resultado and resultado.deleted_count > 0:
            print(f"Usuário {nome_usuario} deletado com sucesso!")
            return True
        print(f"Usuário {nome_usuario} não encontrado para exclusão.")
        return False

    def usuario_existe(self, nome_usuario):
        return (
            self.db_gerencia.find_one(
                self.colecao_nomes, {"nome_usuario": nome_usuario}
            )
            is not None
        )
