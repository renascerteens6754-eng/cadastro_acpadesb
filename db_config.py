from supabase import create_client, Client
import os
import traceback


def connect_db() -> Client:
    """
    Cria e retorna uma conexão com o Supabase
    """
    try:
        # Credenciais do Supabase
        url = "https://jnpkspwxdbiveqkpualb.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpucGtzcHd4ZGJpdmVxa3B1YWxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjAzNjEsImV4cCI6MjA5MTQ5NjM2MX0.tM0fGG0klToWNnt-HHsfT2cpIYTlwxrZRebZ07RSDbI"

        if not url or not key:
            raise Exception("Supabase URL ou KEY não configuradas")

        print(f"🔄 Conectando ao Supabase: {url[:30]}...")

        # Criar cliente
        supabase: Client = create_client(url, key)

        # Testar conexão
        test = supabase.table("congregacoes").select("*").limit(1).execute()
        print("✅ Conexão com Supabase estabelecida com sucesso!")

        return supabase

    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        traceback.print_exc()
        raise e
