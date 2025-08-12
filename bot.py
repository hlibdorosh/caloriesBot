import os
import openai
from openai import AsyncOpenAI
from db import init_db, SessionLocal, Parameters, Intake

from openai_utils import chat_with_openai


from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from meal_analysis import get_meal_conv_handler

from datetime import date, timedelta
from db import SessionLocal, Parameters, DailyLog


load_dotenv()

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

from parameter_handlers import (
    start_height, set_height,
    start_weight, set_weight,
    start_age, set_age,
    start_sex_input, set_sex,
    start_goal_input, set_goal,
    HEIGHT, WEIGHT, AGE, SEX, GOAL
)




# Load .env
load_dotenv()

# Set API keys
HEIGHT, WEIGHT, AGE, SEX, GOAL = range(5)
ASK_GPT = 5
ASK_MEAL_DESCRIPTION = 10


######################/ commands##############################
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 <b>Справка</b>\n\n"
        "<b>Доступные команды и действия:</b>\n"
        "/start – запустить бота и открыть главное меню\n"
        "/help – показать эту справку\n\n"
        "📋 Также можно использовать кнопки:\n"
        "• Установить рост, вес, возраст, пол и цель\n"
        "• Спросить GPT – задать любой вопрос\n"
        "• Добавить приём пищи – бот рассчитает БЖУ и калории\n\n"
        "ℹ️ После каждого добавленного приёма пищи бот считает, сколько вы уже съели за день."
    )
    await update.message.reply_text(help_text, parse_mode="HTML")


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    session = SessionLocal()
    try:
        # текущий пользователь
        user = session.query(Parameters).filter_by(telegram_id=telegram_id).first()
        if not user:
            await update.message.reply_text("📭 Данные о вас не найдены. Сначала задайте параметры.")
            return

        today = date.today()
        consumed = user.consumed_today or 0
        advised = user.daily_calories or 0

        # история за последние 7 дней (без сегодняшнего)
        history = (
            session.query(DailyLog)
            .filter(DailyLog.telegram_id == telegram_id, DailyLog.date < today)
            .order_by(DailyLog.date.desc())
            .limit(7)
            .all()
        )

        msg = [f"📊 *Статистика питания*\n",
               f"Сегодня ({today}): {consumed} / {advised} ккал\n"]

        if history:
            msg.append("\n🗓 История:")
            for h in history:
                msg.append(f"{h.date}: {h.consumed_calories} / {h.advised_calories} ккал")

        await update.message.reply_text("\n".join(msg), parse_mode="Markdown")
    finally:
        session.close()









########################## OpenAI call #######################
async def chat_with_openai(message):
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {str(e)}"


async def start_ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваш вопрос для GPT:")
    return ASK_GPT

async def handle_gpt_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    telegram_id = update.message.from_user.id

    session = SessionLocal()
    user = session.query(Parameters).filter_by(telegram_id=telegram_id).first()
    session.close()

    # Формируем строку с параметрами
    user_context = ""
    if user:
        user_context = (
            f"Информация о пользователе:\n"
            f"- Рост: {user.height} см\n"
            f"- Вес: {user.weight} кг\n"
            f"- Возраст: {user.age} лет\n"
            f"- Пол: {user.sex}\n"
            f"- Цель: {user.goal}\n\n"
            f"- Калории в день: {user.daily_calories} ккал\n\n"
            f"- Потребление сегодня: {user.consumed_today} ккал\n\n"
        )

    # Отправка сообщения в GPT
    full_prompt = user_context + "Вопрос пользователя:\n" + user_input
    await update.message.reply_text("⏳ Ваш диетолог обрабатывает информацию...")

    response = await chat_with_openai(full_prompt)

    await update.message.reply_text(response)

    # Главное меню снова
    keyboard = [
        ["⬆️ Установить рост", "⚖ Установить вес"],
        ["📅 Установить возраст", "🚻 Установить пол"],
        ["🎯 Установить цель", "🤖 Спросить GPT"], ["🍽 Добавить приём пищи"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

    return ConversationHandler.END




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["⬆️ Установить рост", "⚖ Установить вес"],
        ["📅 Установить возраст", "🚻 Установить пол"],
        ["🎯 Установить цель", "🤖 Спросить GPT"], ["🍽 Добавить приём пищи"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите параметр для установки:", reply_markup=markup)


# main
def main():
    init_db()
    app = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    # 👇 Conversation handler ДОЛЖЕН быть ДО run_polling()
    height_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Установить рост"), start_height)],
        states={HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_height)]},
        fallbacks=[]
    )

    weight_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Установить вес"), start_weight)],
        states={WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_weight)]},
        fallbacks=[]
    )

    age_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Установить возраст"), start_age)],
        states={AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_age)]},
        fallbacks=[]
    )

    sex_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Установить пол"), start_sex_input)],
        states={SEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_sex)]},
        fallbacks=[]
    )

    goal_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Установить цель"), start_goal_input)],
        states={GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_goal)]},
        fallbacks=[]
    )

    gpt_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Спросить GPT"), start_ask_gpt)],
        states={ASK_GPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gpt_question)]},
        fallbacks=[]
    )


    app.add_handler(goal_conv)

    # 👉 Сначала регистрируем все хендлеры
    app.add_handler(CommandHandler("start", start))

    # 👉 Только потом запускаем бота
    app.add_handler(height_conv)
    app.add_handler(weight_conv)
    app.add_handler(age_conv)
    app.add_handler(sex_conv)
    app.add_handler(goal_conv)
    app.add_handler(gpt_conv)
    app.add_handler(get_meal_conv_handler())
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", show_stats))

    app.run_polling()


if __name__ == "__main__":
    main()
