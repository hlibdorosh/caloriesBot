from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db import SessionLocal, Parameters
from telegram.ext import ConversationHandler

from db import SessionLocal, Parameters
from utils import calculate_daily_calories

HEIGHT, WEIGHT, AGE, SEX, GOAL = range(5)

# Рост
async def start_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваш рост (в сантиметрах):")
    return HEIGHT

async def set_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = int(update.message.text)
        session = SessionLocal()
        telegram_id = update.message.from_user.id
        user = session.query(Parameters).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = Parameters(telegram_id=telegram_id, height=height)
            session.add(user)
        else:
            user.height = height

        user.daily_calories = calculate_daily_calories(user.weight, user.height, user.age, user.sex, user.goal)
        session.commit()
        session.close()
        await update.message.reply_text("Рост сохранён ✅")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Введите число.")
        return HEIGHT

# Вес
async def start_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваш вес (в килограммах):")
    return WEIGHT

async def set_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text)
        session = SessionLocal()
        telegram_id = update.message.from_user.id
        user = session.query(Parameters).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = Parameters(telegram_id=telegram_id, weight=weight)
            session.add(user)
        else:
            user.weight = weight

        user.daily_calories = calculate_daily_calories(user.weight, user.height, user.age, user.sex, user.goal)
        session.commit()
        session.close()
        await update.message.reply_text("Вес сохранён ✅")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Введите число.")
        return WEIGHT

# Возраст
async def start_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваш возраст (в полных годах):")
    return AGE

async def set_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
        session = SessionLocal()
        telegram_id = update.message.from_user.id
        user = session.query(Parameters).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = Parameters(telegram_id=telegram_id, age=age)
            session.add(user)
        else:
            user.age = age

        user.daily_calories = calculate_daily_calories(user.weight, user.height, user.age, user.sex, user.goal)
        session.commit()
        session.close()
        await update.message.reply_text("Возраст сохранён ✅")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Введите число.")
        return AGE

# Пол
async def start_sex_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Мужской 🚹", "Женский 🚺"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Выберите ваш пол:", reply_markup=markup)
    return SEX

async def set_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sex_text = update.message.text.strip().lower()
    if sex_text not in ["мужской 🚹", "женский 🚺"]:
        await update.message.reply_text("Пожалуйста, выберите вариант с кнопки.")
        return SEX

    session = SessionLocal()
    telegram_id = update.message.from_user.id
    user = session.query(Parameters).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = Parameters(telegram_id=telegram_id, sex=sex_text)
        session.add(user)
    else:
        user.sex = sex_text

    user.daily_calories = calculate_daily_calories(user.weight, user.height, user.age, user.sex, user.goal)
    session.commit()
    session.close()

    await update.message.reply_text("Пол сохранён ✅")

    # ⬇ Показываем главное меню
    keyboard = [
        ["⬆️ Установить рост", "⚖ Установить вес"],
        ["📅 Установить возраст", "🚻 Установить пол"],
        ["🎯 Установить цель", "🤖 Спросить GPT"], ["🍽 Добавить приём пищи"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите следующий параметр:", reply_markup=markup)

    return ConversationHandler.END


# Цель
async def start_goal_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Поддержка ➡️", "Набор массы ⬆️", "Похудение ⬇️"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Выберите вашу цель:", reply_markup=markup)
    return GOAL

async def set_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal_text = update.message.text.strip().lower()
    goal_map = {
        "поддержка ➡️": "maintain",
        "набор массы ⬆️": "gain",
        "похудение ⬇️": "lose"
    }
    if goal_text not in goal_map:
        await update.message.reply_text("Пожалуйста, выберите цель с кнопки.")
        return GOAL
    session = SessionLocal()
    telegram_id = update.message.from_user.id
    user = session.query(Parameters).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = Parameters(telegram_id=telegram_id, goal=goal_map[goal_text])
        session.add(user)
    else:
        user.goal = goal_map[goal_text]

    user.daily_calories = calculate_daily_calories(user.weight, user.height, user.age, user.sex, user.goal)

    session.commit()
    session.close()
    await update.message.reply_text("Цель сохранена ✅")
    keyboard = [
        ["⬆️ Установить рост", "⚖ Установить вес"],
        ["📅 Установить возраст", "🚻 Установить пол"],
        ["🎯 Установить цель", "🤖 Спросить GPT"], ["🍽 Добавить приём пищи"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите следующий параметр:", reply_markup=markup)

    return ConversationHandler.END
    return ConversationHandler.END


