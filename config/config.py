import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DATABASE_USER")
DB_PASS = os.getenv("DATABASE_PASSWORD")
DB_NAME = os.getenv("DATABASE_NAME")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")

GOOGLE_APP_CREDENTIAL = os.getenv("GOOGLE_APP_CREDENTIAL")
OAUTH2_CALLBACK_URL = os.getenv("OAUTH2_CALLBACK_URL")

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")