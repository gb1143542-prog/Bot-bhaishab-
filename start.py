from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from keyboards.menu import (
    start_menu,
    help_category_page,
    help_commands_page,
    render_commands_text,
)

router = Router(name="start")

START_TEXT = (
    "Hey 👋 {fullname}!\n\n"
    "🔹 I'm NeoGuard — POWERFUL Group Management Bot\n"
    "🔹 The most advanced Telegram security & utility bot with tons of features.\n\n"
    "Hit /help to explore full potential!\n"
    "Support: @NeoGuardSupport"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        START_TEXT.format(fullname=message.from_user.full_name),
        reply_markup=start_menu(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("📚 <b>NeoGuard Command Categories</b>", reply_markup=help_category_page(0))


@router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(
        START_TEXT.format(fullname=callback.from_user.full_name),
        reply_markup=start_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("help_page:"))
async def cb_help_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "📚 <b>NeoGuard Command Categories</b>", reply_markup=help_category_page(page)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("help_cat:"))
async def cb_help_category(callback: CallbackQuery):
    _, category, back_page = callback.data.split(":")
    await callback.message.edit_text(
        render_commands_text(category),
        reply_markup=help_commands_page(category, int(back_page)),
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "offers")
async def cb_offers(callback: CallbackQuery):
    await callback.answer("Coming soon 🔥", show_alert=True)
