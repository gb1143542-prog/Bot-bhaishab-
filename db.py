from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, MONGO_DB_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

users_col = db["users"]
chats_col = db["chats"]
warns_col = db["warns"]
filters_col = db["filters"]
mod_logs_col = db["mod_logs"]
game_scores_col = db["game_scores"]
ai_usage_col = db["ai_usage"]
custom_settings_col = db["custom_settings"]
linked_channels_col = db["linked_channels"]


async def upsert_user(user_id: int, chat_id: int, full_name: str, username: str | None):
    """Track a user so features like /masstag have a member list to work with."""
    await users_col.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"full_name": full_name, "username": username}},
        upsert=True,
    )


async def is_module_enabled(chat_id: int, module_name: str, default: bool = True) -> bool:
    doc = await custom_settings_col.find_one({"chat_id": chat_id, "module_name": module_name})
    if doc is None:
        return default
    return bool(doc.get("enabled", default))


async def set_module_enabled(chat_id: int, module_name: str, enabled: bool):
    await custom_settings_col.update_one(
        {"chat_id": chat_id, "module_name": module_name},
        {"$set": {"enabled": enabled}},
        upsert=True,
    )


async def log_mod_action(chat_id: int, actor_id: int, target_id: int, action: str, reason: str = ""):
    await mod_logs_col.insert_one(
        {
            "chat_id": chat_id,
            "actor_id": actor_id,
            "target_id": target_id,
            "action": action,
            "reason": reason,
        }
    )
