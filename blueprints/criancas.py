from flask import Blueprint, request, jsonify
from db_config import connect_db
from datetime import datetime, date
import traceback

criancas_bp = Blueprint(
    "criancas",
    __name__,
    url_prefix="/criancas"
)


# ======================================================
# LISTAR TODOS
# ======================================================
@criancas_bp.route("/", methods=["GET"])
def listar():
    try:
        supabase = connect_db()
        resp = supabase.table("criancas").select("*").order("nome").execute()
        return jsonify(resp.data or []), 200
    except Exception as e:
        print("ERRO LISTAR:", str(e))
        traceback.print_exc()
        return jsonify([]), 200


# ======================================================
# BUSCAR POR NOME
# ======================================================
@criancas_bp.route("/nome/<string:nome>", methods=["GET"])
def buscar_por_nome(nome):
    try:
        supabase = connect_db()
        resp = supabase.table("criancas").select("*").ilike("nome", f"%{nome}%").order("nome").execute()
        return jsonify(resp.data or []), 200
    except Exception as e:
        print("ERRO BUSCAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# CADASTRAR
# ======================================================
@criancas_bp.route("/", methods=["POST"])
def cadastrar():
    try:
        supabase = connect_db()
        data = request.json
        result = supabase.table("criancas").insert(data).execute()
        return jsonify(result.data[0]), 201
    except Exception as e:
        print("ERRO CADASTRAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# ATUALIZAR
# ======================================================
@criancas_bp.route("/<int:id>", methods=["PUT"])
def atualizar(id):
    try:
        supabase = connect_db()
        data = request.json
        resp = supabase.table("criancas").update(data).eq("id", id).execute()
        return jsonify(resp.data[0]), 200
    except Exception as e:
        print("ERRO ATUALIZAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# DELETAR
# ======================================================
@criancas_bp.route("/<int:id>", methods=["DELETE"])
def deletar(id):
    try:
        supabase = connect_db()
        supabase.table("criancas").delete().eq("id", id).execute()
        return jsonify({"ok": True}), 200
    except Exception as e:
        print("ERRO DELETAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# MIGRAR CRIANÇAS (SIMPLIFICADA)
# ======================================================
@criancas_bp.route("/migrar-para-adolescentes", methods=["POST"])
def migrar_para_adolescentes():
    try:
        print("=" * 50)
        print("🚀 INICIANDO MIGRAÇÃO")
        print("=" * 50)

        supabase = connect_db()

        # Buscar crianças
        resp = supabase.table("criancas").select("*").execute()
        criancas = resp.data or []
        print(f"📊 Crianças encontradas: {len(criancas)}")

        if not criancas:
            return jsonify({"status": "ok", "mensagem": "Nenhuma criança", "migradas": []}), 200

        hoje = date.today()
        migradas = []

        for crianca in criancas:
            try:
                data_nasc_str = crianca.get("data_nasc")
                if not data_nasc_str:
                    print(f"⚠️ Sem data: {crianca.get('nome')}")
                    continue

                # Calcular idade
                data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
                idade = hoje.year - data_nasc.year
                if hoje.month < data_nasc.month or (hoje.month == data_nasc.month and hoje.day < data_nasc.day):
                    idade -= 1

                print(f"🔍 {crianca.get('nome')} - Idade: {idade}")

                if idade >= 12:
                    # Preparar dados
                    dados_adolescente = {
                        "nome": crianca.get("nome"),
                        "nome_pai": crianca.get("nome_pai"),
                        "nome_mae": crianca.get("nome_mae"),
                        "cpf": crianca.get("cpf"),
                        "rg": crianca.get("rg"),
                        "contato": crianca.get("contato"),
                        "data_nasc": crianca.get("data_nasc"),
                        "congregacao": crianca.get("congregacao"),
                        "endereco": crianca.get("endereco")
                    }

                    # Inserir em adolescentes
                    insert_result = supabase.table("adolescentes").insert(dados_adolescente).execute()

                    if insert_result.data:
                        # Remover de crianças
                        supabase.table("criancas").delete().eq("id", crianca.get("id")).execute()
                        migradas.append({
                            "id_original": crianca.get("id"),
                            "nome": crianca.get("nome"),
                            "idade": idade
                        })
                        print(f"✅ MIGRADA: {crianca.get('nome')} ({idade} anos)")

            except Exception as e:
                print(f"❌ Erro processando {crianca.get('nome')}: {e}")

        print(f"✅ TOTAL MIGRADAS: {len(migradas)}")
        print("=" * 50)

        return jsonify({
            "status": "ok",
            "mensagem": f"{len(migradas)} criança(s) migrada(s)",
            "migradas": migradas
        }), 200

    except Exception as e:
        print("❌ ERRO NA MIGRAÇÃO:", str(e))
        traceback.print_exc()
        return jsonify({"status": "erro", "erro": str(e)}), 500