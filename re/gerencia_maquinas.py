from gerencia_BD import GerenciadorMongoDB
from bson.objectid import ObjectId


class GerenciadorMaquinas:
    def __init__(self, db_gerencia: GerenciadorMongoDB):
        self.db_gerencia = db_gerencia
        self.colecao_nomes = 'maquinas'

    def adicionar_maquina(self, nome_maquina, id_usuario):
        if not isinstance(id_usuario, ObjectId):
            try:
                id_usuario = ObjectId(id_usuario)
            except:
                print('ID de usuário inválido.')
                return None

        dados_maquina = {'nome_maquina': nome_maquina, 'id_usuario': id_usuario}
        resultado = self.db_gerencia.insert_one(self.colecao_nomes, dados_maquina)
        if not resultado == None and not resultado.inserted_id == None:
            print(
                f'Máquina "{nome_maquina}" adicionada com sucesso para o usuário {id_usuario}!'
            )
            return resultado.inserted_id
        return None

    def listar_maquinas_por_usuario(self, id_usuario):
        if not isinstance(id_usuario, ObjectId):
            try:
                id_usuario = ObjectId(id_usuario)
            except:
                print('ID de usuário inválido.')
                return []

        maquinas = self.db_gerencia.find(self.colecao_nomes, {'id_usuario': id_usuario})
        if maquinas:
            print(f'Máquinas encontradas para o usuário {id_usuario}:')
            for maquina in maquinas:
                print(
                    f'  - ID: {maquina.get('_id')}, Nome: {maquina.get('nome_maquina')}'
                )
            return list(maquinas)
        print(f'Nenhuma máquina encontrada para o usuário {id_usuario}.')
        return []

    def remover_maquina(self, id_maquina):
        if not isinstance(id_maquina, ObjectId):
            try:
                id_maquina = ObjectId(id_maquina)
            except:
                print('ID de máquina inválido.')
                return False

        resultado = self.db_gerencia.delete_one(self.colecao_nomes, {'_id': id_maquina})
        if resultado and resultado.deleted_count > 0:
            print(f'Máquina com ID {id_maquina} removida com sucesso!')
            return True
        print(f'Máquina com ID {id_maquina} não encontrada para exclusão.')
        return False
