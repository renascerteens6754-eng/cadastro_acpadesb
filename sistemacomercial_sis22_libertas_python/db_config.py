from supabase import create_client, Client
import os
import traceback


def connect_db() -> Client:
    """
    Cria e retorna uma conexão com o Supabase
    """
    try:
        # Credenciais do Supabase
        url = "https://nhfpldkvqrvgyddbpbnw.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5oZnBsZGt2cXJ2Z3lkZGJwYm53Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyNTk4MDMsImV4cCI6MjA3NzgzNTgwM30.0weuBxaHTPXhdn6BWjZSAxmG7LpcfVQsJGFTC0KdaAs"

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