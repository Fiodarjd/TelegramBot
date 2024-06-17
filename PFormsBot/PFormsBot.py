
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import os


# Включаем ведение журнала
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для отслеживания диалога
PAID_LUNCH_STATE = 1
FREE_LUNCH_STATE = 2

# Read env from FOODBOT_TOKEN
tokenString = os.environ['FOODBOT_TOKEN']

# Определяем команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.user_data.get('state')

    if state == PAID_LUNCH_STATE:
        # Если пользователь находится в состоянии ввода количества обедов на платной основе
        await update.message.reply_text('Выберите вариант:', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Обеды", callback_data='lunch')],
            [InlineKeyboardButton("Присутствующие", callback_data='attendance')]
        ]))
    elif state == FREE_LUNCH_STATE:
        # Если пользователь находится в состоянии ввода количества обедов на бесплатной основе
        await update.message.reply_text('Выберите вариант:', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Обеды", callback_data='lunch')],
            [InlineKeyboardButton("Присутствующие", callback_data='attendance')]
        ]))
    else:
        # Если пользователь только что начал взаимодействие с ботом
        keyboard = [
            [InlineKeyboardButton("Обеды", callback_data='lunch')],
            [InlineKeyboardButton("Присутствующие", callback_data='attendance')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Приветствую! Чем могу вам помочь?', reply_markup=reply_markup)


# Определяем команду /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('state') is None:
        # Если state ещё не установлено, устанавливаем его в None
        context.user_data['state'] = None
    keyboard = [
        [InlineKeyboardButton("Обеды", callback_data='lunch')],
        [InlineKeyboardButton("Присутствующие", callback_data='attendance')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Список доступных команд:\n/start - Начать разговор со мной\n/help - Получить помощь',
        reply_markup=reply_markup)


# Обработчик нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'lunch':
        # Если пользователь нажал на кнопку "Обеды"
        await query.edit_message_text(text="Сколько на платной основе?")
        context.user_data['state'] = PAID_LUNCH_STATE
    elif query.data == 'attendance':
        # Если пользователь нажал на кнопку "Присутствующие"
        await query.edit_message_text(text="Присутствующие: ...")
    elif query.data == 'menu':
        # Если пользователь нажал на кнопку "Меню"
        await query.edit_message_text(text="Выберите вариант:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Обеды", callback_data='lunch')],
            [InlineKeyboardButton("Присутствующие", callback_data='attendance')]
        ]))


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.user_data.get('state')

    if state == PAID_LUNCH_STATE:
        try:
            paid_lunches = int(update.message.text)
            if paid_lunches == 0:
                context.user_data['paid_attempts'] = context.user_data.get('paid_attempts', 0) + 1
                if context.user_data['paid_attempts'] < 2:
                    await update.message.reply_text("Ошибка, сколько на платной основе?")
                else:
                    await update.message.reply_text("Сколько на бесплатной основе?")
                    context.user_data['state'] = FREE_LUNCH_STATE
            else:
                context.user_data['paid_lunches'] = paid_lunches
                await update.message.reply_text("Сколько на бесплатной основе?")
                context.user_data['state'] = FREE_LUNCH_STATE
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите числовое значение.")
    elif state == FREE_LUNCH_STATE:
        try:
            free_lunches = int(update.message.text)
            context.user_data['free_lunches'] = free_lunches
            paid_lunches = context.user_data.get('paid_lunches', 0)
            await update.message.reply_text(f"На платной основе: {paid_lunches}\nНа бесплатной основе: {free_lunches}",
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Меню", callback_data='menu')]]))
            # Сбрасываем состояние
            context.user_data['state'] = None
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите числовое значение.")


def main() -> None:
    # Токен
    token = tokenString

    # Создаем приложение
    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчик для нажатий на кнопки
    application.add_handler(CallbackQueryHandler(button))

    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
