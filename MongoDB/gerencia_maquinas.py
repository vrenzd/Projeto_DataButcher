from .gerencia_BD import GerenciadorMongoDB
from bson.objectid import ObjectId


class GerenciadorMaquinas:
    def __init__(self, db_gerencia: GerenciadorMongoDB):
        self.db_gerencia = db_gerencia
        self.colecao_nomes = 'maquinas'

    def adicionar_maquina(self, empresa, modelo):  
        dados_maquina = {'fabricante': empresa, 'modelo': modelo}
        resultado = self.db_gerencia.insert_one(self.colecao_nomes, dados_maquina)
        if not resultado == None and not resultado.inserted_id == None:
            print(
                f'Máquina adicionada com sucesso com o código: {resultado.inserted_id}!'
            )
            return resultado.inserted_id
        return None

    def validar_maquina(self, codigo_maquina, nome_maquina, id_usuario):
        query_busca = {'_id': ObjectId(codigo_maquina)}
        maquina = self.db_gerencia.find_one(self.colecao_nomes, query_busca)

        if not maquina:
            print(f'Falha na associação: Máquina com código "{codigo_maquina}" não encontrada.')
            return "Máquina não encontrada.", False

        if maquina.get('id_usuario') is not None:
            if maquina['id_usuario'] == id_usuario:
                print(f'Aviso: Máquina "{codigo_maquina}" já está associada a este usuário.')
                return "Esta máquina já pertence a você.", False
            else:
                print(f'Falha na associação: Máquina "{codigo_maquina}" já pertence a outro usuário.')
                return "Esta máquina já está em uso por outro usuário.", False
            
        query_update = {'_id': maquina['_id']}
        novos_valores = {
                'id_usuario': id_usuario,
                'nome_maquina': nome_maquina,
        }
        
        resultado = self.db_gerencia.update_one(self.colecao_nomes, query_update, novos_valores)

        if resultado and resultado.modified_count > 0:
            print(f'Sucesso! Máquina "{codigo_maquina}" associada ao usuário {id_usuario}.')
            return "Máquina adicionada ao seu perfil com sucesso!", True
        else:
            print(f'Falha na associação: Erro inesperado ao atualizar o banco de dados.')
            return "Ocorreu um erro ao tentar associar a máquina.", False

    def listar_maquinas_por_usuario(self, id_usuario):
        if not isinstance(id_usuario, ObjectId):
            try:
                id_usuario = ObjectId(id_usuario)
            except:
                print('ID de usuário inválido.')
                return []

        maquinas = self.db_gerencia.find(self.colecao_nomes, {'id_usuario': id_usuario})

        if maquinas:
            return maquinas
        else:
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
