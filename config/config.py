import os
from dotenv import load_dotenv

load_dotenv(".env")

DB_USER = os.getenv("DATABASE_USER")
DB_PASS = os.getenv("DATABASE_PASSWORD")
DB_NAME = os.getenv("DATABASE_NAME")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")

GOOGLE_APP_CREDENTIAL = os.getenv("GOOGLE_APP_CREDENTIAL")
GOOGLE_OAUTH2_CALLBACK_URL = os.getenv("GOOGLE_OAUTH2_CALLBACK_URL")

NOTION_OAUTH_CLIENT_ID = os.getenv("NOTION_OAUTH_CLIENT_ID")
NOTION_OAUTH_CLIENT_SECRET = os.getenv("NOTION_OAUTH_CLIENT_SECRET")
NOTION_OAUTH2_CALLBACK_URL = os.getenv("NOTION_OAUTH2_CALLBACK_URL")

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

REDIS_URL = os.getenv("REDIS_URL")

TELEBOT_TOKEN = os.getenv("TELEBOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEBOT_TOKEN}/"
TELEGRAM_SEND_ENDPOINT = f"{TELEGRAM_API}sendMessage"
