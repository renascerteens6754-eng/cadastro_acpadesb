from flask import Blueprint, request, jsonify
from db_config import connect_db
import traceback
from datetime import datetime
import jwt
import os

outros_bp = Blueprint("outros", __name__, url_prefix="/outros")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-muito-forte-aqui-mude-em-producao")


# ======================================================
# FUNÇÃO PARA VALIDAR TOKEN E PERFIL
# ======================================================
def verificar_autorizacao():
    """Retorna (payload, erro) onde erro é uma resposta JSON pronta, se houver."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None, (jsonify({"success": False, "message": "Token não fornecido"}), 401)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"success": False, "message": "Token expirado"}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({"success": False, "message": "Token inválido"}), 401)


# ======================================================
# ROTA PARA LISTAR "OUTROS"
# ======================================================
@outros_bp.route("/", methods=["GET", "OPTIONS"])
def listar_outros():
    if request.method == "OPTIONS":
        return '', 200

    try:
        payload, erro = verificar_autorizacao()
        if erro: return erro

        # Regra de negócio (opcional): líder local não pode ver "outros" se não for do depto dele?
        # Como "outros" não tem departamento por padrão, deixamos todos os perfis visualizarem.
        # Se quiser restringir, adicione aqui.

        supabase = connect_db()
        # Busca todos os registros ordenados por nome
        resp = supabase.table("outros").select("*").order("nome").execute()

        return jsonify(resp.data or []), 200

    except Exception as e:
        print(f"❌ ERRO AO LISTAR OUTROS: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500


# ======================================================
# ROTA PARA CRIAR "OUTRO"
# ======================================================
@outros_bp.route("/", methods=["POST", "OPTIONS"])
def criar_outro():
    if request.method == "OPTIONS":
        return '', 200

    try:
        payload, erro = verificar_autorizacao()
        if erro: return erro

        # Apenas Secretário e Líder Local podem criar (ajuste conforme sua regra)
        if payload.get('perfil') not in ['secretario', 'lider local']:
            return jsonify({"success": False, "message": "Sem permissão para cadastrar"}), 403

        data = request.json

        # Validação mínima
        if not data.get('nome'):
            return jsonify({"success": False, "message": "O nome é obrigatório"}), 400

        novo_registro = {
            "nome": data.get('nome', '').strip(),
            "data_nasc": data.get('data_nasc') or None,
            "cpf": data.get('cpf', '').strip() or None,
            "rg": data.get('rg', '').strip() or None,
            "contato": data.get('contato', '').strip() or None,
            "nome_pai": data.get('nome_pai', '').strip() or None,
            "nome_mae": data.get('nome_mae', '').strip() or None,
            "congregacao": data.get('congregacao', '').strip() or None,
            "endereco": data.get('endereco', '').strip() or None,
            "created_at": datetime.now().isoformat()
        }

        supabase = connect_db()
        result = supabase.table("outros").insert(novo_registro).execute()

        if result.data:
            return jsonify({
                "success": True,
                "message": "Registro cadastrado com sucesso!",
                "data": result.data[0]
            }), 201
        else:
            return jsonify({"success": False, "message": "Erro ao cadastrar"}), 500

    except Exception as e:
        print(f"❌ ERRO AO CRIAR OUTRO: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500


# ======================================================
# ROTA PARA ATUALIZAR "OUTRO"
# ======================================================
@outros_bp.route("/<int:registro_id>", methods=["PUT", "OPTIONS"])
def atualizar_outro(registro_id):
    if request.method == "OPTIONS":
        return '', 200

    try:
        payload, erro = verificar_autorizacao()
        if erro: return erro

        if payload.get('perfil') not in ['secretario', 'lider local']:
            return jsonify({"success": False, "message": "Sem permissão para editar"}), 403

        data = request.json

        if not data.get('nome'):
            return jsonify({"success": False, "message": "O nome é obrigatório"}), 400

        dados_atualizados = {
            "nome": data.get('nome', '').strip(),
            "data_nasc": data.get('data_nasc') or None,
            "cpf": data.get('cpf', '').strip() or None,
            "rg": data.get('rg', '').strip() or None,
            "contato": data.get('contato', '').strip() or None,
            "nome_pai": data.get('nome_pai', '').strip() or None,
            "nome_mae": data.get('nome_mae', '').strip() or None,
            "congregacao": data.get('congregacao', '').strip() or None,
            "endereco": data.get('endereco', '').strip() or None
        }

        supabase = connect_db()

        # Verifica se existe
        check = supabase.table("outros").select("id").eq("id", registro_id).execute()
        if not check.data:
            return jsonify({"success": False, "message": "Registro não encontrado"}), 404

        # Atualiza
        result = supabase.table("outros").update(dados_atualizados).eq("id", registro_id).execute()

        if result.data:
            return jsonify({
                "success": True,
                "message": "Registro atualizado com sucesso!",
                "data": result.data[0]
            }), 200
        else:
            return jsonify({"success": False, "message": "Erro ao atualizar"}), 500

    except Exception as e:
        print(f"❌ ERRO AO ATUALIZAR OUTRO: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500


# ======================================================
# ROTA PARA EXCLUIR "OUTRO"
# ======================================================
@outros_bp.route("/<int:registro_id>", methods=["DELETE", "OPTIONS"])
def excluir_outro(registro_id):
    if request.method == "OPTIONS":
        return '', 200

    try:
        payload, erro = verificar_autorizacao()
        if erro: return erro

        if payload.get('perfil') not in ['secretario', 'lider local']:
            return jsonify({"success": False, "message": "Sem permissão para excluir"}), 403

        supabase = connect_db()

        # Verifica se existe
        check = supabase.table("outros").select("id").eq("id", registro_id).execute()
        if not check.data:
            return jsonify({"success": False, "message": "Registro não encontrado"}), 404

        # Exclui
        supabase.table("outros").delete().eq("id", registro_id).execute()

        return jsonify({"success": True, "message": "Registro excluído com sucesso!"}), 200

    except Exception as e:
        print(f"❌ ERRO AO EXCLUIR OUTRO: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500
