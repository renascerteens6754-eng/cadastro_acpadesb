from flask import Blueprint, request, jsonify
from db_config import connect_db
from datetime import datetime, date
import traceback

adolescentes_bp = Blueprint(
    "adolescentes",
    __name__,
    url_prefix="/adolescentes"
)


# ======================================================
# LISTAR TODOS
# ======================================================
@adolescentes_bp.route("/", methods=["GET"])
def listar():
    try:
        supabase = connect_db()
        resp = supabase.table("adolescentes").select("*").order("nome").execute()
        return jsonify(resp.data or []), 200
    except Exception as e:
        print("ERRO LISTAR:", str(e))
        return jsonify([]), 200


# ======================================================
# BUSCAR POR NOME
# ======================================================
@adolescentes_bp.route("/buscar", methods=["GET"])
def buscar_por_nome():
    try:
        supabase = connect_db()
        nome = request.args.get("nome", "").strip()
        if not nome:
            return jsonify([]), 200
        resp = supabase.table("adolescentes").select("*").ilike("nome", f"%{nome}%").order("nome").execute()
        return jsonify(resp.data or []), 200
    except Exception as e:
        print("ERRO BUSCAR:", str(e))
        return jsonify([]), 200


# ======================================================
# CADASTRAR
# ======================================================
@adolescentes_bp.route("/", methods=["POST"])
def cadastrar():
    try:
        supabase = connect_db()
        data = request.json
        result = supabase.table("adolescentes").insert(data).execute()
        return jsonify(result.data[0]), 201
    except Exception as e:
        print("ERRO CADASTRAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# ATUALIZAR
# ======================================================
@adolescentes_bp.route("/<int:id>", methods=["PUT"])
def atualizar(id):
    try:
        supabase = connect_db()
        data = request.json
        resp = supabase.table("adolescentes").update(data).eq("id", id).execute()
        return jsonify(resp.data[0]), 200
    except Exception as e:
        print("ERRO ATUALIZAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# DELETAR
# ======================================================
@adolescentes_bp.route("/<int:id>", methods=["DELETE"])
def deletar(id):
    try:
        supabase = connect_db()
        supabase.table("adolescentes").delete().eq("id", id).execute()
        return jsonify({"ok": True}), 200
    except Exception as e:
        print("ERRO DELETAR:", str(e))
        return jsonify({"erro": str(e)}), 500


# ======================================================
# DELETAR ADOLESCENTES COM 18 ANOS OU MAIS
# ======================================================
@adolescentes_bp.route("/verificar-e-deletar-maiores", methods=["POST"])
def verificar_e_deletar_maiores():
    try:
        print("=" * 50)
        print("🔍 VERIFICANDO ADOLESCENTES COM 18+ ANOS")
        print("=" * 50)

        supabase = connect_db()

        # Buscar todos os adolescentes
        resp = supabase.table("adolescentes").select("*").execute()
        adolescentes = resp.data or []

        if not adolescentes:
            print("ℹ️ Nenhum adolescente cadastrado.")
            return jsonify({
                "status": "ok",
                "mensagem": "Nenhum adolescente cadastrado",
                "deletados": 0,
                "deletados_lista": []
            }), 200

        print(f"📊 Total de adolescentes encontrados: {len(adolescentes)}")

        hoje = date.today()
        deletados_lista = []

        for adolescente in adolescentes:
            try:
                data_nasc_str = adolescente.get("data_nasc")
                if not data_nasc_str:
                    print(f"⚠️ {adolescente.get('nome')} - sem data de nascimento")
                    continue

                # Converter para date
                if isinstance(data_nasc_str, str):
                    data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
                else:
                    data_nasc = data_nasc_str

                # Calcular idade
                idade = hoje.year - data_nasc.year
                if hoje.month < data_nasc.month or (hoje.month == data_nasc.month and hoje.day < data_nasc.day):
                    idade -= 1

                print(f"🔍 {adolescente.get('nome')} - Nasc: {data_nasc} - Idade: {idade}")

                if idade >= 18:
                    print(f"🗑️ DELETANDO: {adolescente.get('nome')} ({idade} anos)")
                    supabase.table("adolescentes").delete().eq("id", adolescente.get("id")).execute()
                    deletados_lista.append({
                        "id": adolescente.get("id"),
                        "nome": adolescente.get("nome"),
                        "idade": idade
                    })

            except Exception as e:
                print(f"❌ Erro ao processar {adolescente.get('nome')}: {e}")

        print("=" * 50)
        print(f"✅ DELETADOS: {len(deletados_lista)} adolescente(s)")
        print("=" * 50)

        return jsonify({
            "status": "ok",
            "mensagem": f"{len(deletados_lista)} adolescente(s) deletado(s) por terem 18 anos ou mais",
            "deletados": len(deletados_lista),
            "deletados_lista": deletados_lista
        }), 200

    except Exception as e:
        print("❌ ERRO:", str(e))
        traceback.print_exc()
        return jsonify({"status": "erro", "erro": str(e)}), 500
