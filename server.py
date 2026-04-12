from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Importar blueprints
from blueprints.criancas import criancas_bp
from blueprints.adolescentes import adolescentes_bp
from blueprints.congregacoes import congregacoes_bp

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Registrar blueprints
app.register_blueprint(criancas_bp)
app.register_blueprint(adolescentes_bp)
app.register_blueprint(congregacoes_bp)

# ======================================================
# ROTA DE TESTE - ADICIONE AQUI
# ======================================================
@app.route('/ping')
def ping():
    return {"status": "ok", "message": "Servidor rodando!"}

# Rota para servir o index.html
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
