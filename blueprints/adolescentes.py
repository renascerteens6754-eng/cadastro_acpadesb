from flask import Blueprint, request, jsonify
from db_config import connect_db
import traceback
import os

adolescentes_bp = Blueprint("adolescentes", __name__, url_prefix="/adolescentes")

@adolescentes_bp.route("/", methods=["GET"])
def listar():
    try:
        print("📋 LISTANDO ADOLESCENTES...")
        
        # Verifica variáveis antes de conectar
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        print(f"🔍 URL encontrada? {bool(url)}")
        print(f"🔍 KEY encontrada? {bool(key)}")
        
        if not url or not key:
            print("❌ Variáveis de ambiente não encontradas!")
            return jsonify({
                "erro": "Configuração do servidor incompleta",
                "detalhe": "SUPABASE_URL e SUPABASE_KEY não estão configuradas"
            }), 500
        
        supabase = connect_db()
        print("🔄 Executando consulta...")
        
        resp = supabase.table("adolescentes").select("*").order("nome").execute()
        
        print(f"✅ Encontrados {len(resp.data or [])} adolescentes")
        print(f"📊 Dados: {resp.data[:2] if resp.data else []}")  # Mostra até 2 registros
        
        return jsonify(resp.data or []), 200
        
    except Exception as e:
        print("=" * 50)
        print("❌ ERRO NA LISTAGEM:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(traceback.format_exc())
        print("=" * 50)
        
        return jsonify({
            "erro": str(e),
            "tipo": type(e).__name__,
            "detalhe": "Verifique os logs do servidor"
        }), 500
