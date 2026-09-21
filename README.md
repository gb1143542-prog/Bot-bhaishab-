# NeoGuard — Phase 1 + Phase 2

Runnable now: core skeleton, paginated `/help` menu (Phase 1), and the full
Admin & Moderation module (Phase 2): `/ban /unban /mute /unmute /kick /warn
/warns /locks /report /masstag /massaction /admin`.

Other categories (Info, Content, Dev, AI, Play, Anime, Web/Media, Group) show
in the `/help` menu as placeholders — their commands aren't wired up yet;
say "continue from last" to get the next phase.

## Deploy on Render

1. Push this folder to a GitHub repo.
2. On Render: **New → Blueprint**, point it at the repo (`render.yaml` is
   already included) — or **New → Web Service** manually with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`
3. Set these environment variables in Render's dashboard (Environment tab):
   - `BOT_TOKEN` — from @BotFather
   - `MONGO_URI` — a free MongoDB Atlas cluster connection string
   - `OWNER_ID` — your Telegram user ID (defaults to 8757838567)
4. Deploy. Render sets `RENDER_EXTERNAL_URL` and `PORT` automatically — the
   bot detects this and switches itself into webhook mode; no manual
   webhook setup needed.
5. In Telegram, add the bot to a group and promote it to admin (needed for
   ban/mute/kick to work), then run `/start` and `/help`.

## Local testing (no public URL)

Leave `RENDER_EXTERNAL_URL` unset in your local `.env` — `main.py` detects
this and runs in long-polling mode instead of webhook mode.

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in BOT_TOKEN and MONGO_URI
python main.py
```

## Project layout
```
neoguard/
├── main.py              # entrypoint (webhook on Render, polling locally)
├── config.py             # env vars
├── db.py                 # MongoDB collections + helpers
├── handlers/
│   ├── start.py           # /start, paginated /help
│   └── admin.py           # Phase 2: moderation commands
├── keyboards/
│   └── menu.py            # category grid + PREV/NEXT pagination
├── utils/
│   └── permissions.py      # admin/owner checks
├── requirements.txt
├── render.yaml
└── .env.example
```

## Notes
- `Ccgen` is intentionally not implemented (fraud tool).
- `/masstag` only tags users who've sent at least one message in the chat
  since the bot started tracking (Telegram's Bot API has no "list all
  members" call) — capped at 50 per run to avoid flood limits.
- Next build order per the master spec: Info & Lookup → Content Generators
  → Dev Tools → AI (needs cost caps) → Games → Anime/Web-Media/Group Utils.
