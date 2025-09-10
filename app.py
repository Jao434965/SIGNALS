from flask import Flask, request, jsonify

# cria a aplicação Flask
app = Flask(__name__)

# rota inicial (GET)
@app.route('/')
def home():
    return "Servidor Flask no Render rodando!"

# rota para receber sinais (POST)
@app.route('/signal', methods=['POST'])
def signal():
    data = request.json
    print("📩 Sinal recebido:", data)  # aparece nos logs do Render
    return jsonify({"status": "ok", "data": data})

# executa o app localmente (no Render, o gunicorn vai cuidar disso)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
