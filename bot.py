import logging
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

GET_CONTACT = 1

PRIZES = {
    1: "🌸 подарочный сертификат на 3000 рублей",
    2: "🌸 скидка 15% на любую покупку",
    3: "🌸 любое украшение бренда SPARKLE & BASE",
    4: "🌸 подарочный сертификат на 3000 рублей",
    5: "🌸 скидка 15% на любую покупку",
    6: "🌸 любое украшение бренда SPARKLE & BASE"
}

user_rolled = {}

# ===== ВАШИ ДАННЫЕ =====
BOT_TOKEN = "8713653388:AAHIsFenDBXtA4I5VXbgVJhGijvXEqtmkiY"
ADMIN_ID = 5095030147
# =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} запустил бота")
    
    if user_id in user_rolled and user_rolled[user_id]:
        await update.message.reply_text(
            "Вы уже участвовали в розыгрыше! 🎲\n\n"
            "Если Вы ещё не оставили номер телефона, нажмите кнопку ниже, чтобы получить Ваш подарок 👇"
        )
        contact_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📞 Поделиться номером телефона", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text("Нажмите кнопку:", reply_markup=contact_keyboard)
        return GET_CONTACT
    
    welcome_text = (
        "Добро пожаловать в розыгрыш от магазина российских дизайнеров SAINT MAEVE! \n\n"
        "Вы - наше главное вдохновение, и мы рады, что в праздничный день 8 Марта вы присоединились к нашей игре. Бросайте кубик и получите подарок✨"
    )
    keyboard = [[InlineKeyboardButton("🎲 Бросить кубик", callback_data="roll_dice")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def roll_dice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} бросил кубик")
    
    if user_id in user_rolled and user_rolled[user_id]:
        await query.message.reply_text("Вы уже бросали кубик! Используйте кнопку ниже, чтобы получить подарок.")
        return
    
    dice_result = random.randint(1, 6)
    prize = PRIZES[dice_result]
    
    user_rolled[user_id] = True
    context.user_data['prize'] = prize
    
    result_text = (
        f"🎲 Вам выпало число: {dice_result}\n\n"
        f"Ваш подарок: {prize}\n\n"
        f"👇🏻 Чтобы получить приз, нажмите кнопку «Поделиться номером»"
    )
    
    contact_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📞 Поделиться номером телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await query.message.reply_text(result_text, reply_markup=contact_keyboard)
    return GET_CONTACT

# ===== ИСПРАВЛЕННАЯ ФУНКЦИЯ =====
async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("=== ФУНКЦИЯ get_contact ВЫЗВАНА ===")
    
    contact = update.message.contact
    user = update.effective_user
    
    if contact:
        phone = contact.phone_number
        prize = context.user_data.get('prize', 'Не определен')
        
        logger.info(f"✅ Получен номер: {phone} от пользователя {user.id}")
        
        # ИСПРАВЛЕНО: убираем клавиатуру правильным способом
        await update.message.reply_text(
            "⏳ Обрабатываем ваш номер...",
            reply_markup=None  # Просто убираем клавиатуру
        )
        
        # Финальный текст
        final_text = (
            "Спасибо за участие в розыгрыше! 🎉\n\n"
            "Вскоре наш менеджер свяжется с Вами по указанному номеру и уточнит, "
            "когда Вам было бы удобно получить подарок.\n\n"
            "А пока Вы можете подписаться на канал SAINT MAEVE Concept (@stmaeve_concept), "
            "чтобы следить за новостями, или перейти на сайт saintmaeve.ru и выбрать свой новый образ!"
        )
        await update.message.reply_text(final_text)
        
        # Кнопки
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Канал", url="https://t.me/stmaeve_concept")],
            [InlineKeyboardButton("🌐 Сайт", url="https://saintmaeve.ru")]
        ])
        await update.message.reply_text("Полезные ссылки:", reply_markup=buttons)
        
        # Отправка админу
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📞 Новая заявка!\nИмя: {user.first_name}\nТелефон: {phone}\nПриз: {prize}"
            )
            logger.info(f"✅ Уведомление отправлено админу {ADMIN_ID}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки админу: {e}")
    else:
        logger.error("❌ contact is None")
        await update.message.reply_text("Ошибка: не получен номер телефона.")
    
    return ConversationHandler.END
# ===== КОНЕЦ ИСПРАВЛЕНИЯ =====

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("До свидания!")
    return ConversationHandler.END

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text and update.message.text != "/start":
        logger.info(f"Получено сообщение не в диалоге: {update.message.text}")
        await update.message.reply_text("Используйте команду /start для участия в розыгрыше.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(roll_dice_callback, pattern="^roll_dice$")],
        states={GET_CONTACT: [MessageHandler(filters.CONTACT, get_contact)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("✅ Бот SAINT MAEVE запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
