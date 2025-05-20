import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# Chaves
TELEGRAM_TOKEN = "8092738476:AAGzaIjIMyVzc8tuPy065MQqaCC8YG6J9n4"
OPENROUTER_API_KEY = "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"

# Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Menu principal
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 Placar em tempo real", callback_data='placar')],
        [InlineKeyboardButton("💬 Bater papo com o FURIA Bot", callback_data='chat')],
        [InlineKeyboardButton("📅 Próximos jogos", callback_data='jogos')]
    ])

# Início
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['chat_mode'] = False
    texto = (
        "👊 Bem-vindo(a) ao *FURIA CS Fan Bot*!\n\n"
        "Aqui você acompanha placares, jogos e ainda pode bater papo com nosso bot que entende tudo de Counter-Strike e FURIA. Vamos nessa? 🐆🔥"
    )
    await update.message.reply_text(texto, reply_markup=main_menu(), parse_mode="Markdown")

# Botões
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'placar':
        texto = "🎮 *Placar ao vivo:*\nFURIA 2 x 1 NAVI\n🕹️ 2º mapa - Mirage"
        await query.edit_message_text(texto, reply_markup=back_button(), parse_mode="Markdown")

    elif data == 'jogos':
        texto = "📅 *Próximos jogos da FURIA:*\n- vs Liquid: 04/05 às 18h\n- vs G2: 06/05 às 15h"
        await query.edit_message_text(texto, reply_markup=back_button(), parse_mode="Markdown")

    elif data == 'chat':
        context.user_data['chat_mode'] = True
        await query.edit_message_text("💬 Manda aí sua pergunta sobre CS, FURIA ou o cenário competitivo!", reply_markup=back_button())

    elif data == 'voltar':
        context.user_data['chat_mode'] = False
        await query.edit_message_text("🔙 Voltando ao menu principal...", reply_markup=main_menu())

# Botão de voltar
def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Voltar", callback_data='voltar')]])

# IA gratuita com OpenRouter
def openrouter_chat(message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Você é um bot que conversa com fãs do time FURIA de CS:GO. Seja empolgado, informal e entusiasta do cenário competitivo."},
            {"role": "user", "content": message}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Mensagens
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('chat_mode'):
        try:
            user_msg = update.message.text
            reply = openrouter_chat(user_msg)
            await update.message.reply_text(reply)
        except Exception as e:
            await update.message.reply_text(f"Erro ao acessar IA: {str(e)}")
    else:
        await update.message.reply_text("Use /start para voltar ao menu.")

# Execução
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot está rodando...")
    app.run_polling()
