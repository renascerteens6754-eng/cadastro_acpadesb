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

@app.route('/test-supabase-connection')
def test_supabase_connection():
    """Testa a conexão com Supabase"""
    try:
        from db_config import connect_db
        
        # Testa se as variáveis existem
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        resultado = {
            "variaveis_existem": {
                "SUPABASE_URL": bool(url),
                "SUPABASE_KEY": bool(key)
            },
            "url_valor": url if url else "NÃO DEFINIDA",
            "key_prefix": key[:30] + "..." if key else "NÃO DEFINIDA"
        }
        
        # Tenta conectar
        if url and key:
            supabase = connect_db()
            resultado["conexao"] = "✅ Cliente criado"
            
            # Tenta fazer uma consulta simples
            try:
                resp = supabase.table("adolescentes").select("*", count="exact").limit(1).execute()
                resultado["consulta"] = {
                    "sucesso": True,
                    "total_registros": resp.count,
                    "conseguiu_ler": True
                }
            except Exception as e:
                resultado["consulta"] = {
                    "sucesso": False,
                    "erro": str(e)
                }
        else:
            resultado["erro"] = "Variáveis de ambiente não configuradas"
        
        return resultado
        
    except Exception as e:
        import traceback
        return {
            "erro": str(e),
            "traceback": traceback.format_exc()
        }, 500
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
