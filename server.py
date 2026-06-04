from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Tenta carregar .env apenas se estiver em desenvolvimento
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()
    print("📁 Arquivo .env carregado (ambiente local)")

from blueprints.criancas import criancas_bp
from blueprints.adolescentes import adolescentes_bp
from blueprints.congregacoes import congregacoes_bp

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

print(f"🔧 SUPABASE_URL: {'✅ Configurada' if os.getenv('SUPABASE_URL') else '❌ Não encontrada'}")
print(f"🔧 SUPABASE_KEY: {'✅ Configurada' if os.getenv('SUPABASE_KEY') else '❌ Não encontrada'}")

app.register_blueprint(criancas_bp)
app.register_blueprint(adolescentes_bp)
app.register_blueprint(congregacoes_bp)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/ping')
def ping():
    return {"status": "ok", "message": "Servidor rodando!"}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
