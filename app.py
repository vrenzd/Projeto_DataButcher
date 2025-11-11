from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from functools import wraps
import jwt
import datetime
from MongoDB.gerencia_BD import GerenciadorMongoDB
from MongoDB.gerencia_usuario import GerenciaUsuario
from MongoDB.gerencia_maquinas import GerenciadorMaquinas
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import sys

# Carrega variáveis do .env
sys.path.append(os.path.dirname(__file__))
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-padrao')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-chave-secreta')
CORS(app, supports_credentials=True)  # Habilita CORS para o frontend

usuario = os.getenv('MONGO_USER')
senha = os.getenv('MONGO_PASS')
# Inicialização do MongoDB

MONGO_URI = f'mongodb+srv://{usuario}:{senha}@databutcher.ckzgenn.mongodb.net/'
DB_NAME = os.getenv('DB_NAME')

db_gerencia = GerenciadorMongoDB(MONGO_URI, DB_NAME)
db_gerencia.conectar()

# Inicializa gerenciadores
gerencia_usuario = GerenciaUsuario(db_gerencia)
gerencia_maquinas = GerenciadorMaquinas(db_gerencia)

# Decorator para autenticação JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token está faltando!'}), 401
        
        try:
            # Remove o 'Bearer ' do token se presente
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

# Rotas de Autenticação

@app.route('/')
def home():
    return render_template('TelaInicial.html')

@app.route('/machines')
def machines():
    return render_template('machines.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        nome_usuario = data.get('name')
        senha = data.get('password')
        empresa = data.get('company')
        email = data.get('email')
        
        if not nome_usuario or not senha:
            return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400
        
        if gerencia_usuario.cadastrar_usuario(nome_usuario, senha, email, empresa):
            return jsonify({'message': 'Usuário cadastrado com sucesso!'}), 201
        else: 
            return jsonify({'error': 'Erro ao cadastrar usuário'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        nome_usuario = data.get('nome_usuario')
        senha = data.get('senha')
        
        if gerencia_usuario.verificar_usuario(nome_usuario, senha):
            # Buscar usuário para pegar o ID
            user = db_gerencia.find_one('usuarios', {'nome_usuario': nome_usuario})
            
            # Gerar token JWT
            token = jwt.encode({
                'user_id': str(user['_id']),
                'nome_usuario': nome_usuario,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['JWT_SECRET_KEY'], algorithm="HS256")
            
            return jsonify({
                'message': 'Login realizado com sucesso!',
                'token': token,
                'user_id': str(user['_id']),
                'nome_usuario': nome_usuario
            }), 200
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rotas de Máquinas (Protegidas)
@app.route('/api/machines', methods=['POST'])
@token_required
def add_machine(current_user_id):
    try:
        data = request.get_json()
        nome_maquina = data.get('nome_maquina')
        codigo = data.get('codigo')
        
        if not nome_maquina:
            return jsonify({'error': 'Nome da máquina é obrigatório'}), 400
        
        machine_id = gerencia_maquinas.adicionar_maquina(nome_maquina, ObjectId(current_user_id))
        
        if machine_id:
            return jsonify({
                'message': 'Máquina adicionada com sucesso!',
                'machine_id': str(machine_id)
            }), 201
        else:
            return jsonify({'error': 'Erro ao adicionar máquina'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/machines', methods=['GET'])
@token_required
def list_machines(current_user_id):
    try:
        maquinas = gerencia_maquinas.listar_maquinas_por_usuario(ObjectId(current_user_id))
        if maquinas is None:
            return jsonify({'error': 'Erro ao buscar máquinas'}), 500
        
        maquina_list = []
        try:
            for maquina in maquinas:
                maquina_list.append({
                    '_id': str(maquina['_id']),
                    'nome_maquina': maquina.get('nome_maquina',''),
                    'id_usuario': str(maquina.get('id_usuario', ''))
                })
            print(f'Processado todas as máquinas deste usuário.')
            return jsonify({'machines': maquina_list}), 200
        finally:
            maquinas.close()

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/machines/<machine_id>', methods=['DELETE'])
@token_required
def remove_machine(current_user_id, machine_id):
    try:
        # Verificar se a máquina pertence ao usuário antes de remover
        maquina = db_gerencia.find_one('maquinas', {
            '_id': ObjectId(machine_id),
            'id_usuario': ObjectId(current_user_id)
        })
        
        if not maquina:
            return jsonify({'error': 'Máquina não encontrada ou não pertence ao usuário'}), 404
        
        if gerencia_maquinas.remover_maquina(ObjectId(machine_id)):
            return jsonify({'message': 'Máquina removida com sucesso!'}), 200
        else:
            return jsonify({'error': 'Erro ao remover máquina'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para dados dos sensores
@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """
    Endpoint para receber dados dos sensores IoT
    Não requer autenticação JWT, mas pode usar API key
    """
    try:
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['maquina_id', 'tensao', 'vibracao', 'temperatura', 'rpm']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se a máquina existe
        maquina = db_gerencia.find_one('maquinas', {'_id': ObjectId(data['maquina_id'])})
        if not maquina:
            return jsonify({'error': 'Máquina não encontrada'}), 404
        
        # Preparar documento para inserção
        sensor_data = {
            'maquina_id': ObjectId(data['maquina_id']),
            'usuario_id': maquina['id_usuario'],
            'dados_sensor': {
                'tensao': data['tensao'],
                'vibracao': data['vibracao'],
                'temperatura': data['temperatura'],
                'rpm': data['rpm']
            },
            'timestamp': datetime.datetime.utcnow(),
            'metadata': data.get('metadata', {})
        }
        
        # Inserir na coleção de dados dos sensores
        resultado = db_gerencia.insert_one('dados_sensores', sensor_data)
        
        if resultado:
            return jsonify({
                'message': 'Dados do sensor recebidos com sucesso!',
                'sensor_data_id': str(resultado.inserted_id)
            }), 201
        else:
            return jsonify({'error': 'Erro ao salvar dados do sensor'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensor-data/<machine_id>', methods=['GET'])
@token_required
def get_sensor_data(current_user_id, machine_id):
    """
    Buscar dados dos sensores de uma máquina específica
    """
    try:
        # Verificar se a máquina pertence ao usuário
        maquina = db_gerencia.find_one('maquinas', {
            '_id': ObjectId(machine_id),
            'id_usuario': ObjectId(current_user_id)
        })
        
        if not maquina:
            return jsonify({'error': 'Máquina não encontrada'}), 404
        
        # Buscar dados dos sensores (últimas 100 leituras)
        dados_sensores = db_gerencia.find('dados_sensores', {
            'maquina_id': ObjectId(machine_id)
        }).sort('timestamp', -1).limit(100)
        
        dados_list = []
        for dado in dados_sensores:
            dados_list.append({
                'timestamp': dado['timestamp'].isoformat(),
                'dados_sensor': dado['dados_sensor'],
                'sensor_data_id': str(dado['_id'])
            })
        
        return jsonify({'sensor_data': dados_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API está funcionando!'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)