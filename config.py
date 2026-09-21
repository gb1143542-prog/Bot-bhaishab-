import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "8757838567"))
MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "neoguard")

# Render sets this automatically; used to build the webhook URL
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}" if RENDER_EXTERNAL_URL else ""

# Render injects PORT automatically; default for local runs
PORT = int(os.getenv("PORT", "10000"))

WARN_LIMIT = int(os.getenv("WARN_LIMIT", "3"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is not set")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI env var is not set")
