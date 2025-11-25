from MongoDB.gerencia_BD import GerenciadorMongoDB
from MongoDB.gerencia_usuario import GerenciaUsuario
from MongoDB.gerencia_maquinas import GerenciadorMaquinas
from bson.objectid import ObjectId
import os
import sys
from dotenv import load_dotenv
import qrcode

sys.path.append(os.path.dirname(__file__))
load_dotenv()

usuario = os.getenv('MONGO_USER')
senha = os.getenv('MONGO_PASS')

MONGO_URI = f'mongodb+srv://{usuario}:{senha}@databutcher.ckzgenn.mongodb.net/'
DB_NAME = os.getenv('DB_NAME')

def gerar_qrcode(codigo):
    cod = codigo
    qr = qrcode.QRCode()
    qr.add_data(cod)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    nome_arquivo = f'./Qrcode/qrcode_{cod}.png'
    img.save(nome_arquivo)
    print(f'QR Code salvo com sucesso.')

def main():
    db_gerencia = GerenciadorMongoDB(MONGO_URI, DB_NAME)
    db_gerencia.conectar()

    if db_gerencia.db == None:
        print('Não foi possível conectar ao banco de dados. Encerrando aplicação.')
        return

    genrecia_usuario = GerenciaUsuario(db_gerencia)
    gerencia_maquinas = GerenciadorMaquinas(db_gerencia)

    id_usuario_atual = None

    while True:
        print('\n--- Menu Principal ---')
        print('1 - Cadastrar Usuário')
        print('2 - Login')
        print('3 - Excluir Usuário')
        print('8 - Cadastro de máquina por empresa')
        if id_usuario_atual:
            print('4 - Adicionar Máquina')
            print('5 - Listar Minhas Máquinas')
            print('6 - Remover Máquina')
            print('7 - Logout')
        print('0 - Sair')

        entrada = input('Escolha uma opção: ')

        match entrada:
            case '1':
                nome_usuario = input('Usuário: ')
                senha = input('Senha: ')
                genrecia_usuario.cadastrar_usuario(nome_usuario, senha)

            case '2':
                nome_usuario = input('Usuário: ')
                senha = input('Senha: ')
                if genrecia_usuario.verificar_usuario(nome_usuario, senha):
                    user = db_gerencia.find_one(
                        'usuarios', {'nome_usuario': nome_usuario}
                    )
                    id_usuario_atual = user['_id']
                    print(f'Logado como {nome_usuario} (ID: {id_usuario_atual})')
                else:
                    id_usuario_atual = None

            case '3':
                nome_usuario = input('Usuário a ser excluído: ')
                genrecia_usuario.deletar_usuario(nome_usuario)
                if (
                    id_usuario_atual
                    and genrecia_usuario.db_gerencia.find_one(
                        'usuarios', {'_id': id_usuario_atual}
                    )
                    is None
                ):
                    id_usuario_atual = None

            case '4' if id_usuario_atual:
                nome_maquina = input('Nome da Máquina: ')
                gerencia_maquinas.adicionar_maquina(nome_maquina, id_usuario_atual)

            case '5' if id_usuario_atual:
                gerencia_maquinas.listar_maquinas_por_usuario(id_usuario_atual)

            case '6' if id_usuario_atual:
                id_maquina_str = input('ID da Máquina a ser removida: ')
                try:
                    gerencia_maquinas.remover_maquina(id_maquina_str)
                except Exception:
                    print('ID de máquina inválido.')

            case '7' if id_usuario_atual:
                id_usuario_atual = None
                print('Logout realizado com sucesso.')

            case '8':
                nome_empresa = input('Empresa: ')
                modelo = input('Modelo: ')
                id = gerencia_maquinas.adicionar_maquina(nome_empresa, modelo)
                gerar_qrcode(id)
                print(id)

            case '0':
                print('Saindo...')
                break

            case _:
                print('Opção inválida. Tente novamente.')

    db_gerencia.close()


if __name__ == '__main__':
    main()
