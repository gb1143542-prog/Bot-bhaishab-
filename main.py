import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler

from config import BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_URL, PORT
from handlers import start, admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neoguard")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(admin.router)  # keep last: its catch-all tracker sits at module end


async def on_startup(app: web.Application):
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
        logger.info("Webhook set to %s", WEBHOOK_URL)
    else:
        logger.warning("RENDER_EXTERNAL_URL not set — webhook not configured. Falling back to polling.")


async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()


async def health(request: web.Request):
    return web.Response(text="NeoGuard is alive ✅")


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", health)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


async def run_polling():
    """Local/dev fallback when no public URL is available for a webhook."""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    if WEBHOOK_URL:
        web.run_app(build_app(), host="0.0.0.0", port=PORT)
    else:
        import asyncio

        asyncio.run(run_polling())
