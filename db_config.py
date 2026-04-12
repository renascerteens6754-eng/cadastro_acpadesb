import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def connect_db() -> Client:
    url = os.environ.get("https://jnpkspwxdbiveqkpualb.supabase.co")
    key = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpucGtzcHd4ZGJpdmVxa3B1YWxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjAzNjEsImV4cCI6MjA5MTQ5NjM2MX0.tM0fGG0klToWNnt-HHsfT2cpIYTlwxrZRebZ07RSDbI")

    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórias")

    return create_client(url, key)
