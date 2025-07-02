import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # tu dominio de Vercel

# CoinGecko
cg = CoinGeckoAPI()

# Mapeo de símbolos
SYMBOLS = {
    'BTCUSDT': 'bitcoin',
    'ETHUSDT': 'ethereum',
    'ADAUSDT': 'cardano',
    'BNBUSDT': 'binancecoin',
    'SOLUSDT': 'solana',
    'XRPUSDT': 'ripple'
}

# FastAPI app
app = FastAPI()

# Telegram app
telegram_app = Application.builder().token(TOKEN).build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy RandyTrader (webhook).\n"
        "Escribe el símbolo (BTCUSDT, ETHUSDT...) para ver precio."
    )

async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    if symbol not in SYMBOLS:
        await update.message.reply_text(
            f"❌ Símbolo no soportado: {symbol}.\n"
            "Usa BTCUSDT, ETHUSDT, ADAUSDT, etc."
        )
        return

    coin_id = SYMBOLS[symbol]
    price_data = cg.get_price(ids=coin_id, vs_currencies='usd')
    price = price_data[coin_id]['usd']
    precio_formateado = f"{price:,.2f}"
    await update.message.reply_text(
        f"📈 {symbol}: **${precio_formateado} USD**",
        parse_mode="Markdown"
    )

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))

# Endpoint webhook
@app.post("/webhook")
async def process_webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return {"ok": True}

# Endpoint raíz para test
@app.get("/")
async def root():
    return {"message": "RandyTrader online"}

# Configura webhook solo si lo corres localmente para test
import asyncio

async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    await telegram_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}")

asyncio.run(set_webhook())
