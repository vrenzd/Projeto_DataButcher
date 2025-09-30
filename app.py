
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Conexão com MongoDB local (ajuste se usar Atlas)
client = MongoClient("mongodb://localhost:27017/")
db = client["iot"]
colecao = db["leituras"]

@app.route("/dados", methods=["POST"])
def receber_dados():
    dados = request.get_json()

    # Adiciona timestamp do servidor, se necessário
    dados["recebido_em"] = datetime.utcnow().isoformat()

    # Insere no MongoDB
    colecao.insert_one(dados)

    print("Dados recebidos:", dados)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True)
