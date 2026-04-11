from flask import Blueprint, request, jsonify
from db_config import connect_db
import traceback

congregacoes_bp = Blueprint(
    "congregacoes",
    __name__,
    url_prefix="/congregacoes"
)


# ======================================================
# LISTAR TODAS
# ======================================================
@congregacoes_bp.route("/", methods=["GET"])
def listar():
    try:
        supabase = connect_db()
        resp = supabase.table("congregacoes").select("*").order("nome").execute()

        dados = resp.data if resp.data else []

        resultado = []
        for item in dados:
            resultado.append({
                "id": item.get("id"),
                "nome": item.get("nome")
            })

        return jsonify(resultado), 200

    except Exception as e:
        print("ERRO LISTAR CONGREGAÇÕES:", str(e))
        traceback.print_exc()
        return jsonify([]), 200


# ======================================================
# CADASTRAR
# ======================================================
@congregacoes_bp.route("/", methods=["POST"])
def cadastrar():
    try:
        supabase = connect_db()
        data = request.get_json()

        if not data or not data.get("nome"):
            return jsonify({"erro": "Nome é obrigatório"}), 400

        nova = {"nome": data.get("nome").strip()}
        resp = supabase.table("congregacoes").insert(nova).execute()

        if not resp.data:
            return jsonify({"erro": "Erro ao inserir"}), 400

        return jsonify({
            "id": resp.data[0].get("id"),
            "nome": resp.data[0].get("nome")
        }), 201

    except Exception as e:
        print("ERRO CADASTRAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# ATUALIZAR
# ======================================================
@congregacoes_bp.route("/<int:id>", methods=["PUT"])
def atualizar(id):
    try:
        supabase = connect_db()
        data = request.get_json()

        if not data or not data.get("nome"):
            return jsonify({"erro": "Nome é obrigatório"}), 400

        # Verificar se existe
        check = supabase.table("congregacoes").select("*").eq("id", id).execute()
        if not check.data:
            return jsonify({"erro": "Congregação não encontrada"}), 404

        atualizada = {"nome": data.get("nome").strip()}
        resp = supabase.table("congregacoes").update(atualizada).eq("id", id).execute()

        return jsonify({
            "id": resp.data[0].get("id"),
            "nome": resp.data[0].get("nome")
        }), 200

    except Exception as e:
        print("ERRO ATUALIZAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# DELETAR
# ======================================================
@congregacoes_bp.route("/<int:id>", methods=["DELETE"])
def deletar(id):
    try:
        supabase = connect_db()

        # Verificar se existem registros vinculados
        check_adolescentes = supabase.table("adolescentes").select("id").eq("congregacao", id).execute()
        check_criancas = supabase.table("criancas").select("id").eq("congregacao", id).execute()

        if check_adolescentes.data and len(check_adolescentes.data) > 0:
            return jsonify({"erro": "Existem adolescentes vinculados a esta congregação"}), 400
        if check_criancas.data and len(check_criancas.data) > 0:
            return jsonify({"erro": "Existem crianças vinculadas a esta congregação"}), 400

        supabase.table("congregacoes").delete().eq("id", id).execute()

        return jsonify({"ok": True, "mensagem": "Congregação excluída"}), 200

    except Exception as e:
        print("ERRO DELETAR:", str(e))
        return jsonify({"erro": str(e)}), 500