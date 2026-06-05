from flask import Blueprint, request, jsonify
from db_config import connect_db
import traceback
import json

adolescentes_bp = Blueprint("adolescentes", __name__, url_prefix="/adolescentes")

@adolescentes_bp.route("/", methods=["GET", "OPTIONS"])
def listar():
    if request.method == "OPTIONS":
        return '', 200
    
    try:
        print("📋 GET /adolescentes/ - Listando...")
        supabase = connect_db()
        resp = supabase.table("adolescentes").select("*").order("nome").execute()
        print(f"✅ Encontrados {len(resp.data or [])} registros")
        return jsonify(resp.data or []), 200
    except Exception as e:
        print(f"❌ Erro no GET: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"erro": str(e)}), 500

@adolescentes_bp.route("/", methods=["POST", "OPTIONS"])
def cadastrar():
    if request.method == "OPTIONS":
        return '', 200
    
    try:
        print("=" * 50)
        print("📝 POST /adolescentes/ - Cadastrando...")
        
        # Log do request
        print(f"📌 Content-Type: {request.headers.get('Content-Type')}")
        print(f"📌 Dados recebidos: {request.json}")
        
        data = request.json
        
        # Validação básica
        if not data:
            return jsonify({"erro": "Nenhum dado enviado"}), 400
        
        if not data.get('nome'):
            return jsonify({"erro": "Campo nome é obrigatório"}), 400
        
        # Remove ID se existir (deixa o Supabase gerar)
        if 'id' in data:
            del data['id']
        
        print(f"📌 Dados limpos para inserir: {data}")
        
        supabase = connect_db()
        result = supabase.table("adolescentes").insert(data).execute()
        
        print(f"✅ Inserido com sucesso! ID: {result.data[0].get('id')}")
        print("=" * 50)
        
        return jsonify(result.data[0]), 201
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ ERRO NO POST: {type(e).__name__}")
        print(f"❌ Mensagem: {str(e)}")
        print(traceback.format_exc())
        print("=" * 50)
        
        return jsonify({
            "erro": str(e),
            "tipo": type(e).__name__
        }), 500

@adolescentes_bp.route("/<int:id>", methods=["PUT", "OPTIONS"])
def atualizar(id):
    if request.method == "OPTIONS":
        return '', 200
    
    try:
        print(f"📝 PUT /adolescentes/{id} - Atualizando...")
        data = request.json
        supabase = connect_db()
        resp = supabase.table("adolescentes").update(data).eq("id", id).execute()
        print(f"✅ Atualizado com sucesso!")
        return jsonify(resp.data[0]), 200
    except Exception as e:
        print(f"❌ Erro no PUT: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"erro": str(e)}), 500

@adolescentes_bp.route("/<int:id>", methods=["DELETE", "OPTIONS"])
def deletar(id):
    if request.method == "OPTIONS":
        return '', 200
    
    try:
        print(f"🗑️ DELETE /adolescentes/{id} - Deletando...")
        supabase = connect_db()
        supabase.table("adolescentes").delete().eq("id", id).execute()
        print(f"✅ Deletado com sucesso!")
        return jsonify({"ok": True}), 200
    except Exception as e:
        print(f"❌ Erro no DELETE: {str(e)}")
        return jsonify({"erro": str(e)}), 500
