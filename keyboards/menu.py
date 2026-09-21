from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Module registry: category label -> list of (command, description)
MODULES: dict[str, list[tuple[str, str]]] = {
    "1-Admin": [
        ("/ban", "Ban a user"),
        ("/unban", "Unban a user"),
        ("/mute", "Mute a user"),
        ("/unmute", "Unmute a user"),
        ("/kick", "Kick a user"),
        ("/warn", "Warn a user"),
        ("/warns", "Check warn count"),
        ("/locks", "Toggle chat locks"),
        ("/report", "Report a message to admins"),
        ("/masstag", "Tag all known members"),
        ("/massaction", "Bulk warn/mute/ban"),
        ("/admin", "Admin command list"),
    ],
    "2-Info": [("/weather", "Weather lookup"), ("/crypto", "Crypto prices"), ("/wikipedia", "Wikipedia search")],
    "3-Content": [("/quotes", "Random quote"), ("/joke", "Random joke"), ("/facts", "Random fact")],
    "4-Dev": [("/calculator", "Math evaluator"), ("/qrcode", "Generate QR code"), ("/passwordgen", "Password generator")],
    "5-AI": [("/chatgpt", "Ask the AI"), ("/aiimage", "Generate an image"), ("/tts", "Text to speech")],
    "6-Play": [("/dice", "Roll dice"), ("/truth", "Truth prompt"), ("/couple", "Match two users")],
    "7-Anime": [("/anime", "Anime lookup"), ("/memes", "Random meme")],
    "8-Web/Media": [("/webss", "Website screenshot"), ("/translator", "Translate text")],
    "9-Group": [("/welcome", "Welcome settings"), ("/group", "Group info"), ("/choose", "Pick a random option")],
}

CATEGORY_NAMES = list(MODULES.keys())
PAGE_SIZE = 4  # categories per help page


def start_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ ADD ME IN YOUR GROUP ➕", url="https://t.me/NeoGuardBot?startgroup=true")
    kb.button(text="📚 HELP & COMMANDS", callback_data="help_page:0")
    kb.button(text="🔥 OFFERS / SHOPPING 🔥", callback_data="offers")
    kb.button(text="🧑‍💻 DEVELOPER", url="tg://user?id=8757838567")
    kb.button(text="🤝 SUPPORT", url="https://t.me/NeoGuardSupport")
    kb.adjust(1, 1, 1, 2)
    return kb.as_markup()


def help_category_page(page: int) -> InlineKeyboardMarkup:
    total_pages = max(1, -(-len(CATEGORY_NAMES) // PAGE_SIZE))
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    chunk = CATEGORY_NAMES[start : start + PAGE_SIZE]

    kb = InlineKeyboardBuilder()
    for name in chunk:
        kb.button(text=name, callback_data=f"help_cat:{name}:{page}")
    kb.adjust(2)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅ PREV", callback_data=f"help_page:{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="NEXT ➡", callback_data=f"help_page:{page+1}"))
    kb.row(*nav_row)
    kb.row(InlineKeyboardButton(text="🏠 BACK TO START", callback_data="back_to_start"))
    return kb.as_markup()


def help_commands_page(category: str, back_page: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="⬅ BACK TO CATEGORIES", callback_data=f"help_page:{back_page}"))
    kb.row(InlineKeyboardButton(text="🏠 BACK TO START", callback_data="back_to_start"))
    return kb.as_markup()


def render_commands_text(category: str) -> str:
    lines = [f"📂 <b>{category}</b>\n"]
    for cmd, desc in MODULES.get(category, []):
        lines.append(f"• <code>{cmd}</code> — {desc}")
    return "\n".join(lines)
