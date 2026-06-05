from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Só carrega .env se existir (local)
if os.path.exists('.env'):
    load_dotenv()

from blueprints.criancas import criancas_bp
from blueprints.adolescentes import adolescentes_bp
from blueprints.congregacoes import congregacoes_bp

app = Flask(__name__, static_folder='static', static_url_path='')

# Configuração CORS completa
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Debug das variáveis
print("=" * 50)
print("🔧 CONFIGURAÇÃO DO SERVIDOR")
print(f"📌 SUPABASE_URL: {'✅ Configurada' if os.getenv('SUPABASE_URL') else '❌ FALTANDO'}")
print(f"📌 SUPABASE_KEY: {'✅ Configurada' if os.getenv('SUPABASE_KEY') else '❌ FALTANDO'}")
print("=" * 50)

app.register_blueprint(criancas_bp)
app.register_blueprint(adolescentes_bp)
app.register_blueprint(congregacoes_bp)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/ping')
def ping():
    return {"status": "ok", "message": "Servidor rodando!"}

# Rota de diagnóstico
@app.route('/debug')
def debug():
    return {
        "supabase_url_exists": bool(os.getenv("SUPABASE_URL")),
        "supabase_key_exists": bool(os.getenv("SUPABASE_KEY")),
        "blueprints": ["criancas", "adolescentes", "congregacoes"]
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
