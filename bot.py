from dotenv import load_dotenv
load_dotenv()  # Загружает переменные из .env
import os
import logging  # все персонажи работают
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,  # Вместо CallbackContext
)
import cowsay
import nest_asyncio

nest_asyncio.apply()

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Доступные персонажи
COWSAY_CHARACTERS = ['beavis', 'cheese', 'cow', 'daemon', 'dragon', 'fox', 'ghostbusters',
                     'kitty', 'meow', 'miki', 'milk', 'octopus', 'pig', 'stegosaurus',
                     'stimpy', 'trex', 'turkey', 'turtle', 'tux', 'VOVKA']

# Ссылка на изображение VOVKA
VOVKA_IMAGE_URL = "http://velotes.com/images/i_am/I_am_V_02_resize.jpg"

# Словарь для хранения выбранных персонажей пользователями
user_choices = {}


# Функция для старта
async def start(update: Update, context: ContextTypes) -> None:
    await update.message.reply_text("Привет! Используй /menu, чтобы выбрать персонажа! "
                                    "Если не хочешь выбирать, пиши что-нибудь в чат, будет говорить корова!")


# Функция для вызова меню
async def show_menu(update: Update, context: ContextTypes) -> None:
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = [[InlineKeyboardButton(animal, callback_data=animal)] for animal in COWSAY_CHARACTERS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери персонажа:", reply_markup=reply_markup)


# Обработчик выбора персонажа
async def button(update: Update, context: ContextTypes) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chosen_animal = query.data

    if chosen_animal == 'VOVKA':
        try:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=VOVKA_IMAGE_URL,
                caption="Вот ваш VOVKA! 🎉"
            )
            user_choices[user_id] = 'VOVKA'  # Запоминаем выбор
            await query.edit_message_text(text="Вы выбрали VOVKA! Теперь можете писать сообщения (но он покажет только изображение).")
        except Exception as e:
            logger.error(f"Ошибка при отправке изображения: {e}")
            await query.edit_message_text(text="Не удалось загрузить изображение VOVKA. Попробуйте позже.")
    elif chosen_animal in COWSAY_CHARACTERS:
        user_choices[user_id] = chosen_animal
        await query.edit_message_text(text=f"Ты выбрал: {chosen_animal}. Теперь отправь мне сообщение!")


# Обработчик сообщений
# Обработчик сообщений
async def echo(update: Update, context: ContextTypes) -> None:
    user_id = update.message.from_user.id
    text = update.message.text

    # Проверяем, выбран ли персонаж
    animal = user_choices.get(user_id, 'cow')  # По умолчанию 'cow'

    # Если выбран VOVKA - отправляем его изображение снова
    if animal == 'VOVKA':
        try:
            await context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=VOVKA_IMAGE_URL,
                caption="Вот снова ваш VOVKA! 🎉"
            )
            return  # Прерываем выполнение, чтобы не показывать текстовое сообщение
        except Exception as e:
            logger.error(f"Ошибка при отправке изображения VOVKA: {e}")
            await update.message.reply_text("Не удалось отправить изображение VOVKA 😢")
            return

    # Обработка остальных персонажей
    if hasattr(cowsay, animal):
        cow_message = cowsay.get_output_string(animal, text)
    else:
        cow_message = f"Ошибка! {animal} не найден в cowsay."

    escaped_message = escape_markdown(cow_message)
    await update.message.reply_text(f"```\n{escaped_message}\n```", parse_mode="MarkdownV2")

# Основная функция
def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")

    # Создаём приложение вместо Updater
    app = Application.builder().token(token).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", show_menu))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    print("Бот запущен...")
    app.run_polling()

def escape_markdown(text: str) -> str:
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

if __name__ == '__main__':
    main()
# app.run_polling()  # запуск бота