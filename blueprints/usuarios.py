from flask import Blueprint, request, jsonify, session
from db_config import connect_db
import traceback
import os
from datetime import datetime, timedelta
import jwt

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-muito-forte-aqui-mude-em-producao")

# ======================================================
# PERFIS DISPONÍVEIS
# ======================================================
PERFIS = {
    'secretario': 'Secretário - Acesso a todas as funções',
    'lider regional': 'Líder Regional - Acesso às congregações da sua região',
    'lider local': 'Líder Local - Acesso às congregações do seu respectivo departamento',
    'outro': 'Outro - Acesso apenas visualização'
}

# ======================================================
# DEPARTAMENTOS DISPONÍVEIS
# ======================================================
DEPARTAMENTOS = {
    'infantil': 'Infantil',
    'adolescentes': 'Adolescentes'
}


# ======================================================
# FUNÇÃO PARA VALIDAR SENHA (3 caracteres)
# ======================================================
def validar_senha(senha):
    """Valida se a senha atende aos requisitos (exatamente 3 caracteres)"""
    if len(senha) != 3:
        return False, "A senha deve ter exatamente 3 caracteres"
    if not senha.isalnum():
        return False, "A senha deve conter apenas letras e números"
    return True, ""


# ======================================================
# ROTA DE LOGIN
# ======================================================
@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return '', 200

    try:
        print("=" * 50)
        print("🔐 TENTATIVA DE LOGIN")

        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')

        print(f"📌 Usuário: {username}")

        if not username or not password:
            return jsonify({
                "success": False,
                "message": "Usuário e senha são obrigatórios"
            }), 400

        supabase = connect_db()
        resp = supabase.table("usuario").select("*").eq("username", username).execute()
        usuarios = resp.data or []

        if not usuarios:
            print("❌ Usuário não encontrado")
            return jsonify({
                "success": False,
                "message": "Usuário ou senha inválidos"
            }), 401

        usuario = usuarios[0]

        senha_armazenada = usuario.get('password', '')
        print(f"📌 Senha armazenada: {senha_armazenada}")

        if password != senha_armazenada:
            print("❌ Senha incorreta")
            return jsonify({
                "success": False,
                "message": "Usuário ou senha inválidos"
            }), 401

        perfil = usuario.get('perfil', 'outro')
        departamento = usuario.get('departamento', '')

        # Gerar token JWT
        token = jwt.encode({
            'id': usuario.get('id'),
            'username': usuario.get('username'),
            'perfil': perfil,
            'departamento': departamento,
            'exp': datetime.utcnow() + timedelta(hours=8)
        }, SECRET_KEY, algorithm='HS256')

        print(f"✅ Login bem-sucedido: {username} - Perfil: {perfil} - Departamento: {departamento or 'N/A'}")
        print("=" * 50)

        usuario_sem_senha = {k: v for k, v in usuario.items() if k != 'password'}

        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "token": token,
            "usuario": usuario_sem_senha,
            "perfil": perfil,
            "departamento": departamento
        }), 200

    except Exception as e:
        print(f"❌ ERRO NO LOGIN: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500


# ======================================================
# ROTA PARA CRIAR CONTA (AUTO-REGISTRO)
# ======================================================
@auth_bp.route("/criar-conta", methods=["POST", "OPTIONS"])
def criar_conta():
    """Permite que qualquer usuário crie sua própria conta"""
    if request.method == "OPTIONS":
        return '', 200

    try:
        print("=" * 50)
        print("📝 CRIANDO NOVA CONTA")

        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        confirmar_senha = data.get('confirmar_senha', '')
        perfil = data.get('perfil', 'outro')
        departamento = data.get('departamento', '')

        print(f"📌 Usuário solicitado: {username}")
        print(f"📌 Perfil solicitado: {perfil}")
        print(f"📌 Departamento solicitado: {departamento}")

        # Validações básicas
        if not username or not password:
            return jsonify({
                "success": False,
                "message": "Usuário e senha são obrigatórios"
            }), 400

        # Validar tamanho do username
        if len(username) < 3:
            return jsonify({
                "success": False,
                "message": "O usuário deve ter pelo menos 3 caracteres"
            }), 400

        # Validar senha (exatamente 3 caracteres)
        senha_valida, msg_senha = validar_senha(password)
        if not senha_valida:
            return jsonify({
                "success": False,
                "message": msg_senha
            }), 400

        # Confirmar senha
        if password != confirmar_senha:
            return jsonify({
                "success": False,
                "message": "As senhas não coincidem"
            }), 400

        # Validar perfil permitido para auto-registro
        perfis_permitidos = ['secretario', 'lider regional', 'lider local', 'outro']
        if perfil not in perfis_permitidos:
            return jsonify({
                "success": False,
                "message": f"Perfil inválido. Perfis permitidos: {', '.join(perfis_permitidos)}"
            }), 400

        # Validar departamento (se fornecido)
        if departamento and departamento not in ['infantil', 'adolescentes']:
            return jsonify({
                "success": False,
                "message": "Departamento inválido. Valores permitidos: infantil, adolescentes"
            }), 400

        supabase = connect_db()

        # Verificar se usuário já existe
        resp = supabase.table("usuario").select("*").eq("username", username).execute()
        if resp.data:
            return jsonify({
                "success": False,
                "message": "Nome de usuário já existe. Escolha outro."
            }), 409

        # Criar novo usuário
        novo_usuario = {
            "username": username,
            "password": password,
            "perfil": perfil,
            "departamento": departamento if departamento else None,
            "created_at": datetime.now().isoformat()
        }

        result = supabase.table("usuario").insert(novo_usuario).execute()

        if result.data:
            print(f"✅ Conta criada com sucesso: {username} - Perfil: {perfil} - Departamento: {departamento or 'N/A'}")
            print("=" * 50)

            usuario_criado = result.data[0]
            usuario_sem_senha = {k: v for k, v in usuario_criado.items() if k != 'password'}

            return jsonify({
                "success": True,
                "message": "Conta criada com sucesso! Faça login para continuar.",
                "usuario": usuario_sem_senha
            }), 201
        else:
            return jsonify({
                "success": False,
                "message": "Erro ao criar conta. Tente novamente."
            }), 500

    except Exception as e:
        print(f"❌ ERRO AO CRIAR CONTA: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500


# ======================================================
# ROTA DE VERIFICAÇÃO DE TOKEN
# ======================================================
@auth_bp.route("/verificar", methods=["GET", "OPTIONS"])
def verificar_token():
    if request.method == "OPTIONS":
        return '', 200

    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({
                "authenticated": False,
                "message": "Token não fornecido"
            }), 401

        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        return jsonify({
            "authenticated": True,
            "usuario_id": payload.get('id'),
            "username": payload.get('username'),
            "perfil": payload.get('perfil'),
            "departamento": payload.get('departamento', '')
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({
            "authenticated": False,
            "message": "Token expirado"
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            "authenticated": False,
            "message": "Token inválido"
        }), 401
    except Exception as e:
        return jsonify({
            "authenticated": False,
            "message": str(e)
        }), 500


# ======================================================
# ROTA DE LOGOUT
# ======================================================
@auth_bp.route("/logout", methods=["POST", "OPTIONS"])
def logout():
    if request.method == "OPTIONS":
        return '', 200

    return jsonify({
        "success": True,
        "message": "Logout realizado com sucesso"
    }), 200


# ======================================================
# ROTA PARA LISTAR PERFIS DISPONÍVEIS
# ======================================================
@auth_bp.route("/perfis", methods=["GET", "OPTIONS"])
def listar_perfis():
    if request.method == "OPTIONS":
        return '', 200

    return jsonify({
        "success": True,
        "perfis": PERFIS
    }), 200


# ======================================================
# ROTA PARA LISTAR DEPARTAMENTOS DISPONÍVEIS
# ======================================================
@auth_bp.route("/departamentos", methods=["GET", "OPTIONS"])
def listar_departamentos():
    if request.method == "OPTIONS":
        return '', 200

    return jsonify({
        "success": True,
        "departamentos": DEPARTAMENTOS
    }), 200


# ======================================================
# ROTA PARA LISTAR USUÁRIOS (APENAS SECRETARIO)
# ======================================================
@auth_bp.route("/usuarios", methods=["GET", "OPTIONS"])
def listar_usuarios():
    if request.method == "OPTIONS":
        return '', 200

    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({"success": False, "message": "Token não fornecido"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if payload.get('perfil') not in ['secretario']:
                return jsonify({"success": False, "message": "Apenas secretários podem listar usuários"}), 403
        except:
            return jsonify({"success": False, "message": "Token inválido"}), 401

        supabase = connect_db()
        resp = supabase.table("usuario").select("id, username, perfil, departamento, created_at").execute()

        return jsonify({
            "success": True,
            "usuarios": resp.data or []
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ======================================================
# ROTA PARA EXCLUIR USUÁRIO (APENAS SECRETARIO)
# ======================================================
@auth_bp.route("/usuario/<int:usuario_id>", methods=["DELETE", "OPTIONS"])
def excluir_usuario(usuario_id):
    if request.method == "OPTIONS":
        return '', 200

    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({"success": False, "message": "Token não fornecido"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if payload.get('perfil') != 'secretario':
                return jsonify({"success": False, "message": "Apenas secretários podem excluir usuários"}), 403
        except:
            return jsonify({"success": False, "message": "Token inválido"}), 401

        supabase = connect_db()

        if usuario_id == payload.get('id'):
            return jsonify({"success": False, "message": "Não é possível excluir seu próprio usuário"}), 403

        supabase.table("usuario").delete().eq("id", usuario_id).execute()

        return jsonify({"success": True, "message": "Usuário excluído com sucesso"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ======================================================
# ROTA PARA ATUALIZAR DEPARTAMENTO DO USUÁRIO
# ======================================================
@auth_bp.route("/atualizar-departamento", methods=["PUT", "OPTIONS"])
def atualizar_departamento():
    """Atualiza o departamento do usuário logado"""
    if request.method == "OPTIONS":
        return '', 200

    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({"success": False, "message": "Token não fornecido"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            usuario_id = payload.get('id')
        except:
            return jsonify({"success": False, "message": "Token inválido"}), 401

        data = request.json
        departamento = data.get('departamento', '')

        if not departamento:
            return jsonify({"success": False, "message": "Departamento é obrigatório"}), 400

        if departamento not in ['infantil', 'adolescentes']:
            return jsonify({
                "success": False,
                "message": "Departamento inválido. Valores permitidos: infantil, adolescentes"
            }), 400

        supabase = connect_db()

        # Verificar se o usuário existe
        resp = supabase.table("usuario").select("*").eq("id", usuario_id).execute()
        if not resp.data:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 404

        # Atualizar departamento
        result = supabase.table("usuario").update({"departamento": departamento}).eq("id", usuario_id).execute()

        if result.data:
            return jsonify({
                "success": True,
                "message": f"Departamento atualizado para {departamento} com sucesso",
                "departamento": departamento
            }), 200
        else:
            return jsonify({"success": False, "message": "Erro ao atualizar departamento"}), 500

    except Exception as e:
        print(f"❌ ERRO AO ATUALIZAR DEPARTAMENTO: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ======================================================
# ROTA PARA LISTAR USUÁRIOS POR DEPARTAMENTO
# ======================================================
@auth_bp.route("/usuarios/departamento/<string:departamento>", methods=["GET", "OPTIONS"])
def listar_usuarios_por_departamento(departamento):
    if request.method == "OPTIONS":
        return '', 200

    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({"success": False, "message": "Token não fornecido"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if payload.get('perfil') not in ['secretario', 'lider regional']:
                return jsonify({"success": False, "message": "Sem permissão para listar usuários por departamento"}), 403
        except:
            return jsonify({"success": False, "message": "Token inválido"}), 401

        if departamento not in ['infantil', 'adolescentes']:
            return jsonify({
                "success": False,
                "message": "Departamento inválido. Valores permitidos: infantil, adolescentes"
            }), 400

        supabase = connect_db()
        resp = supabase.table("usuario").select("id, username, perfil, departamento, created_at").eq("departamento", departamento).execute()

        return jsonify({
            "success": True,
            "departamento": departamento,
            "total": len(resp.data or []),
            "usuarios": resp.data or []
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
