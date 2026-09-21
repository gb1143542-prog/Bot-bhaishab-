from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner
from config import OWNER_ID


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def is_chat_admin(message: Message) -> bool:
    """True if the command issuer is an admin/owner of the group, or the bot owner."""
    if message.from_user is None:
        return False
    if is_owner(message.from_user.id):
        return True
    if message.chat.type == "private":
        return False
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))


async def bot_is_admin(message: Message) -> bool:
    """True if NeoGuard itself has admin rights in this chat (needed to ban/mute/kick)."""
    me = await message.bot.get_me()
    member = await message.bot.get_chat_member(message.chat.id, me.id)
    return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))


def get_target_user_id(message: Message) -> int | None:
    """Resolve the target of a moderation command: reply > @username/id arg."""
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1 and parts[1].strip().lstrip("-").isdigit():
            return int(parts[1].strip())
    return None
