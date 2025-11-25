import os
from dotenv import load_dotenv

load_dotenv()

CONFLUENCE_DOMAIN = os.getenv("CONFLUENCE_DOMAIN")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

DATABASE_URL = os.getenv("DATABASE_URL")

HF_API_TOKEN = os.getenv("HF_API_TOKEN")