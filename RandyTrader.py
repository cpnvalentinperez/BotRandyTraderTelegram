import os
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Cargar .env si tienes otras variables (p. ej. TELEGRAM_TOKEN)
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Cliente CoinGecko
cg = CoinGeckoAPI()

# Diccionario simple para mapear tickers a IDs de CoinGecko
SYMBOLS = {
    'BTCUSDT': 'bitcoin',
    'ETHUSDT': 'ethereum',
    'ADAUSDT': 'cardano',
    'BNBUSDT': 'binancecoin',
    'SOLUSDT': 'solana',
    'XRPUSDT': 'ripple'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['BTCUSDT', 'ETHUSDT'],
        ['ADAUSDT', 'BNBUSDT'],
        ['SOLUSDT', 'XRPUSDT']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 ¡Hola! Soy RandyTrader.\n"
        "📊 Elige un par tocando un botón o escríbelo (ej: BTCUSDT):",
        reply_markup=reply_markup
    )

async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()

    if symbol not in SYMBOLS:
        await update.message.reply_text(
            f"❌ Símbolo no soportado: {symbol}.\n"
            "Usa /start para ver los pares disponibles."
        )
        return

    coin_id = SYMBOLS[symbol]
    try:
        price_data = cg.get_price(ids=coin_id, vs_currencies='usd')
        price = price_data[coin_id]['usd']
        precio_formateado = f"{price:,.2f}"
        await update.message.reply_text(
            f"📈 {symbol}: **${precio_formateado} USD**",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))
    print("✅ RandyTrader con CoinGecko está online...")
    app.run_polling()
