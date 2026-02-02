import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHAT_ID_TO_CHECK=os.getenv("CHAT_ID_TO_CHECK")

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
BASE_URL = os.getenv("BASE_URL")
WEBHOOK_PATH = f"/{BOT_TOKEN}"
