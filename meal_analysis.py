# meal_analysis.py
import os
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters, ConversationHandler
from openai_utils import chat_with_openai
from utils import add_calories_with_rollover

from utils import extract_calories
from db import SessionLocal, Parameters

from dotenv import load_dotenv

import base64
load_dotenv()

ASK_MEAL_DESCRIPTION = 10

def get_meal_conv_handler():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Добавить приём пищи"), ask_for_meal)],
        states={
            ASK_MEAL_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_meal_text)]
        },
        fallbacks=[]
    )

# функция ask_for_meal
async def ask_for_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опишите приём пищи (например: «Курица 200 г, рис 150 г, салат»):")
    return ASK_MEAL_DESCRIPTION


async def handle_meal_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    prompt = (
        "Проанализируй следующий приём пищи и оцени содержание БЖУ и калорий.\n"
        "❗️Ответ строго без пояснений, без промежуточных расчётов, только результат.\n"
        "❗️Только 4 строки в формате:\n"
        "Белки: __ г\nЖиры: __ г\nУглеводы: __ г\nКалории: __ ккал\n\n"
        f"Приём пищи: {user_input}"
    )

    try:
        await update.message.reply_text("⏳ Ваш диетолог обрабатывает информацию...")

        # один вызов GPT
        gpt_answer = await chat_with_openai(prompt)
        await update.message.reply_text(gpt_answer)

        # извлекаем калории
        calories = extract_calories(gpt_answer)

        # прибавляем РОВНО ОДИН РАЗ — через утилиту с переносом по дням
        telegram_id = update.message.from_user.id
        add_calories_with_rollover(telegram_id, calories)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка анализа: {e}")

    # главное меню
    keyboard = [
        ["⬆️ Установить рост", "⚖ Установить вес"],
        ["📅 Установить возраст", "🚻 Установить пол"],
        ["🎯 Установить цель", "🤖 Спросить GPT"], ["🍽 Добавить приём пищи"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

    return ConversationHandler.END
