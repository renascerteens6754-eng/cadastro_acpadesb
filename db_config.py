import os
from supabase import create_client
import traceback

def connect_db():
    """Conecta ao Supabase com validação"""
    
    # Tenta diferentes nomes de variáveis
    url = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_URL_CORRECT")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLIC_KEY")
    
    # Debug no servidor (vai aparecer nos logs do Render)
    print("=" * 50)
    print("🔧 TENTANDO CONECTAR AO SUPABASE")
    print(f"📌 URL: {url if url else '❌ NÃO ENCONTRADA'}")
    print(f"📌 KEY: {'✅ ENCONTRADA' if key else '❌ NÃO ENCONTRADA'}")
    print("=" * 50)
    
    # Validações
    if not url:
        erro = "❌ SUPABASE_URL não encontrada nas variáveis de ambiente"
        print(erro)
        raise Exception(erro)
    
    if not key:
        erro = "❌ SUPABASE_KEY não encontrada nas variáveis de ambiente"
        print(erro)
        raise Exception(erro)
    
    # Limpa a URL se necessário
    url = url.strip()
    if url.endswith('/'):
        url = url[:-1]
    if url.endswith('/rest/v1'):
        url = url.replace('/rest/v1', '')
    
    print(f"✅ URL limpa: {url}")
    print(f"✅ Tentando conectar...")
    
    try:
        client = create_client(url, key)
        print("✅ Conexão com Supabase estabelecida com sucesso!")
        return client
    except Exception as e:
        print(f"❌ Erro ao criar cliente: {str(e)}")
        print(traceback.format_exc())
        raise
