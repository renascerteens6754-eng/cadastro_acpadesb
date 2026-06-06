from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()

from blueprints.criancas import criancas_bp
from blueprints.adolescentes import adolescentes_bp
from blueprints.congregacoes import congregacoes_bp

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# DEBUG: Verifique se as variáveis existem
print("=== VERIFICANDO VARIÁVEIS DE AMBIENTE ===")
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", "OK" if os.getenv("SUPABASE_KEY") else "NÃO ENCONTRADA")
print("==========================================")

app.register_blueprint(criancas_bp)
app.register_blueprint(adolescentes_bp)
app.register_blueprint(congregacoes_bp)

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # ← ALTERE AQUI

app.register_blueprint(criancas_bp)
app.register_blueprint(adolescentes_bp)
app.register_blueprint(congregacoes_bp)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/ping')
def ping():
    return {"status": "ok", "message": "Servidor rodando!"}


@app.route('/debug-env')
def debug_env():
    """Mostra todas as variáveis de ambiente (sem expor a chave completa)"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    return {
        "supabase_url_exists": bool(supabase_url),
        "supabase_url_value": supabase_url[:50] + "..." if supabase_url else None,
        "supabase_key_exists": bool(supabase_key),
        "supabase_key_prefix": supabase_key[:20] + "..." if supabase_key else None,
        "todas_variaveis": list(os.environ.keys()),  # Mostra nomes de todas as variáveis
        "python_path": os.getenv("PYTHONPATH"),
        "port": os.getenv("PORT")
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
