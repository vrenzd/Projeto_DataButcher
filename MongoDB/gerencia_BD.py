from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi

class GerenciadorMongoDB:
    def __init__(self, uri, nome_banco):
        self.uri = uri
        self.nome_banco = nome_banco
        self.cliente = None
        self.bd = None
        self.db = None

    def conectar(self):
        try:
            self.cliente = MongoClient(self.uri, server_api=ServerApi('1'))
            self.cliente.admin.command('ping')
            self.bd = self.cliente[self.nome_banco]
            self.db = self.bd
            print('Conexão com MongoDB estabelecida com sucesso!')
        except ConnectionFailure as e:
            print(f'Erro ao conectar ao MongoDB: {e}')
            self.cliente = None
            self.bd = None
            self.db = None

    def fechar(self):
        if self.cliente:
            self.cliente.close()
            self.db = None
            print('Conexão com MongoDB fechada.')

    def obter_colecao(self, nome_colecao):
        if not self.bd == None:
            return self.bd[nome_colecao]
        else:
            print('Erro: Não há conexão com o banco de dados.')
            return None

    def inserir_um(self, nome_colecao, documento):
        colecao = self.obter_colecao(nome_colecao)
        if not colecao == None:
            return colecao.insert_one(documento)
        return None

    def buscar_um(self, nome_colecao, consulta):
        colecao = self.obter_colecao(nome_colecao)
        if not colecao == None:
            return colecao.find_one(consulta)
        return None

    def atualizar_um(self, nome_colecao, consulta, novos_valores):
        colecao = self.obter_colecao(nome_colecao)
        if colecao:
            return colecao.update_one(consulta, {'$set': novos_valores})
        return None

    def deletar_um(self, nome_colecao, consulta):
        colecao = self.obter_colecao(nome_colecao)
        if not colecao == None:
            return colecao.delete_one(consulta)
        return None

    def buscar(self, nome_colecao, consulta=None):
        if consulta is None:
            consulta = {}
        colecao = self.obter_colecao(nome_colecao)
        if not colecao == None:
            return colecao.find(consulta)
        return None

    def connect(self):
        return self.conectar()

    def close(self):
        return self.fechar()

    def get_collection(self, nome_colecao):
        return self.obter_colecao(nome_colecao)

    def insert_one(self, nome_colecao, documento):
        return self.inserir_um(nome_colecao, documento)

    def find_one(self, nome_colecao, consulta):
        return self.buscar_um(nome_colecao, consulta)

    def update_one(self, nome_colecao, consulta, novos_valores):
        return self.atualizar_um(nome_colecao, consulta, novos_valores)

    def delete_one(self, nome_colecao, consulta):
        return self.deletar_um(nome_colecao, consulta)

    def find(self, nome_colecao, consulta=None):
        return self.buscar(nome_colecao, consulta)
