from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions

from config import WARN_LIMIT
from db import warns_col, custom_settings_col, log_mod_action, users_col, upsert_user
from utils.permissions import is_chat_admin, bot_is_admin, get_target_user_id

router = Router(name="admin")

MUTED_PERMISSIONS = ChatPermissions(can_send_messages=False)
UNMUTED_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_other_messages=True,
)


def _admin_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        if not await is_chat_admin(message):
            await message.reply("❌ This command is restricted to chat admins.")
            return
        if not await bot_is_admin(message):
            await message.reply("⚠️ I need to be an admin in this chat to do that.")
            return
        return await func(message, *args, **kwargs)

    return wrapper


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.reply(
        "🛡 <b>Admin Commands</b>\n"
        "/ban /unban /mute /unmute /kick /warn /warns /locks /report /masstag /massaction"
    )


@router.message(Command("ban"))
@_admin_only
async def cmd_ban(message: Message):
    target_id = get_target_user_id(message)
    if not target_id:
        await message.reply("Reply to a user or pass their user ID to ban.")
        return
    await message.chat.ban(target_id)
    await log_mod_action(message.chat.id, message.from_user.id, target_id, "ban")
    await message.reply(f"🔨 Banned user <code>{target_id}</code>.")


@router.message(Command("unban"))
@_admin_only
async def cmd_unban(message: Message):
    target_id = get_target_user_id(message)
    if not target_id:
        await message.reply("Reply to a user or pass their user ID to unban.")
        return
    await message.chat.unban(target_id)
    await log_mod_action(message.chat.id, message.from_user.id, target_id, "unban")
    await message.reply(f"✅ Unbanned user <code>{target_id}</code>.")


@router.message(Command("mute"))
@_admin_only
async def cmd_mute(message: Message):
    target_id = get_target_user_id(message)
    if not target_id:
        await message.reply("Reply to a user or pass their user ID to mute.")
        return
    await message.bot.restrict_chat_member(message.chat.id, target_id, MUTED_PERMISSIONS)
    await log_mod_action(message.chat.id, message.from_user.id, target_id, "mute")
    await message.reply(f"🔇 Muted user <code>{target_id}</code>.")


@router.message(Command("unmute"))
@_admin_only
async def cmd_unmute(message: Message):
    target_id = get_target_user_id(message)
    if not target_id:
        await message.reply("Reply to a user or pass their user ID to unmute.")
        return
    await message.bot.restrict_chat_member(message.chat.id, target_id, UNMUTED_PERMISSIONS)
    await log_mod_action(message.chat.id, message.from_user.id, target_id, "unmute")
    await message.reply(f"🔊 Unmuted user <code>{target_id}</code>.")


@router.message(Command("kick"))
@_admin_only
async def cmd_kick(message: Message):
    target_id = get_target_user_id(message)
    if not target_id:
        await message.reply("Reply to a user or pass their user ID to kick.")
        return
    await message.chat.ban(target_id)
    await message.chat.unban(target_id)  # ban+unban = kick (doesn't stay banned)
    await log_mod_action(message.chat.id, message.from_user.id, target_id, "kick")
    await message.reply(f"👢 Kicked user <code>{target_id}</code>.")


@router.message(Command("warn"))
@_admin_only
async def cmd_warn(message: Message):
    target_id = get_target_user_id(message)
    if not target_id:
        await message.reply("Reply to a user or pass their user ID to warn.")
        return

    doc = await warns_col.find_one_and_update(
        {"chat_id": message.chat.id, "user_id": target_id},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True,
    )
    count = doc["count"] if doc else 1
    await log_mod_action(message.chat.id, message.from_user.id, target_id, "warn")

    if count >= WARN_LIMIT:
        await message.bot.restrict_chat_member(message.chat.id, target_id, MUTED_PERMISSIONS)
        await warns_col.update_one(
            {"chat_id": message.chat.id, "user_id": target_id}, {"$set": {"count": 0}}
        )
        await message.reply(
            f"⚠️ User <code>{target_id}</code> reached {WARN_LIMIT} warns and has been auto-muted."
        )
    else:
        await message.reply(f"⚠️ Warned user <code>{target_id}</code> ({count}/{WARN_LIMIT}).")


@router.message(Command("warns"))
async def cmd_warns(message: Message):
    target_id = get_target_user_id(message) or message.from_user.id
    doc = await warns_col.find_one({"chat_id": message.chat.id, "user_id": target_id})
    count = doc["count"] if doc else 0
    await message.reply(f"User <code>{target_id}</code> has {count}/{WARN_LIMIT} warns.")


@router.message(Command("locks"))
@_admin_only
async def cmd_locks(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or parts[2].lower() not in ("on", "off"):
        await message.reply("Usage: /locks <links|media|forward> <on|off>")
        return
    lock_type, state = parts[1], parts[2].lower()
    await custom_settings_col.update_one(
        {"chat_id": message.chat.id, "module_name": f"lock_{lock_type}"},
        {"$set": {"enabled": state == "on"}},
        upsert=True,
    )
    await message.reply(f"🔒 Lock '{lock_type}' turned {state}.")


@router.message(Command("report"))
async def cmd_report(message: Message):
    if not message.reply_to_message:
        await message.reply("Reply to the message you want to report.")
        return
    await message.reply("🚨 Reported to admins.")
    # Admins get pinged by Telegram's tag mechanism; a full implementation
    # would fetch get_chat_administrators() and @mention each one here.


@router.message(Command("masstag"))
@_admin_only
async def cmd_masstag(message: Message):
    cursor = users_col.find({"chat_id": message.chat.id}).limit(50)  # rate-limit-safe cap
    mentions = []
    async for u in cursor:
        mentions.append(f'<a href="tg://user?id={u["user_id"]}">\u2063</a>')
    if not mentions:
        await message.reply("No known members to tag yet — they need to have sent a message first.")
        return
    await message.reply("📢 " + "".join(mentions), disable_notification=False)


@router.message(Command("massaction"))
@_admin_only
async def cmd_massaction(message: Message):
    await message.reply(
        "Usage: reply to a message with /massaction <warn|mute|ban> to apply it to the sender, "
        "or extend this handler to accept a list of user IDs for true bulk actions."
    )


@router.message()
async def track_user_activity(message: Message):
    """Passively records chat members so /masstag has someone to tag.
    Registered LAST and with no Command filter, so every /command above
    still matches first — this only fires on messages nothing else caught.
    """
    if message.from_user and message.chat.type != "private":
        await upsert_user(
            message.from_user.id, message.chat.id, message.from_user.full_name, message.from_user.username
        )
