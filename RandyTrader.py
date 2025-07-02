import os
from dotenv import load_dotenv
from binance.client import Client
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 📌 1. Carga las variables del archivo .env
load_dotenv()

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# 📌 2. Instancia del cliente de Binance
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# ✅ 3. Comando /start ➜ muestra un teclado con pares comunes
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['BTCUSDT', 'ETHUSDT'],
        ['ADAUSDT', 'BNBUSDT'],
        ['SOLUSDT', 'XRPUSDT']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 ¡Hola! Soy RandyTrader.\n"
        "📊 Elige un par de criptomonedas tocando un botón o escríbelo:\n"
        "(Ejemplo: BTCUSDT, ETHUSDT)",
        reply_markup=reply_markup
    )

# ✅ 4. Manejar cualquier texto ➜ trata el texto como símbolo a consultar
async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        price_float = float(ticker['price'])
        precio_formateado = f"{price_float:,.2f}"
        await update.message.reply_text(
            f"📈 El precio actual de {symbol} es **${precio_formateado}**",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ No pude obtener el precio para *{symbol}*.\n"
            f"Verifica el par e intenta nuevamente.",
            parse_mode="Markdown"
        )

# ✅ 5. Configuración principal del bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))

    print("✅ RandyTrader está escuchando en Telegram...")
    app.run_polling()
