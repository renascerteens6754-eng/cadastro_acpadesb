from flask import Blueprint, request, jsonify, session
from db_config import connect_db
import traceback
import os
from datetime import datetime, timedelta
import jwt

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-muito-forte-aqui-mude-em-producao")

# ======================================================
# PERFIS DISPONÍVEIS (conforme a imagem)
# ======================================================
PERFIS = {
    'secretario': 'Secretário - Acesso a todas as funções',
    'lider regional': 'Líder Regional - Acesso às congregações da sua região',
    'lider local': 'Líder Local - Acesso às congregações do seu respectivo departamento',
    'outro': 'Outro - Acesso apenas visualização'
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

        # Gerar token JWT
        token = jwt.encode({
            'id': usuario.get('id'),
            'username': usuario.get('username'),
            'perfil': perfil,
            'exp': datetime.utcnow() + timedelta(hours=8)
        }, SECRET_KEY, algorithm='HS256')

        print(f"✅ Login bem-sucedido: {username} - Perfil: {perfil}")
        print("=" * 50)

        usuario_sem_senha = {k: v for k, v in usuario.items() if k != 'password'}

        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "token": token,
            "usuario": usuario_sem_senha,
            "perfil": perfil
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

        print(f"📌 Usuário solicitado: {username}")
        print(f"📌 Perfil solicitado: {perfil}")

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

        supabase = connect_db()

        # Verificar se usuário já existe
        resp = supabase.table("usuario").select("*").eq("username", username).execute()
        if resp.data:
            return jsonify({
                "success": False,
                "message": "Nome de usuário já existe. Escolha outro."
            }), 409

        # Criar novo usuário (password char(3) - exatamente 3 caracteres)
        novo_usuario = {
            "username": username,
            "password": password,  # Senha com exatamente 3 caracteres
            "perfil": perfil,
            "created_at": datetime.now().isoformat()
        }

        result = supabase.table("usuario").insert(novo_usuario).execute()

        if result.data:
            print(f"✅ Conta criada com sucesso: {username} - Perfil: {perfil}")
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
            "perfil": payload.get('perfil')
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
# ROTA PARA LISTAR USUÁRIOS (APENAS ADMIN - secretario)
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
        resp = supabase.table("usuario").select("id, username, perfil, created_at").execute()

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
